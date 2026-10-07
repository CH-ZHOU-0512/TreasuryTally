async (page) => {
  const config = __M14_CONFIG__;
  const results = [];
  page.setDefaultTimeout(15000);
  const record = (id, status, evidence, reason = "") => results.push({ id, status, evidence, reason });
  const check = async (id, action) => {
    try { record(id, "PASS", await action()); }
    catch (error) { record(id, "FAIL", { message: String(error.message).slice(0, 350) }, "assertion failed"); }
  };
  const ensure = (value, message) => { if (!value) throw new Error(message); };
  const screen = async (name) => {
    const path = `${config.output}/${name}.png`;
    await page.screenshot({ path, fullPage: true });
    return path;
  };
  await page.getByText("上传报表", { exact: true }).first().waitFor({ timeout: 45000 });
  await page.getByText("运行配置", { exact: true }).click();
  await page.getByRole("textbox", { name: "工作区 ID", exact: true }).fill(config.workspace);
  await page.getByRole("textbox", { name: "工作区 ID", exact: true }).press("Enter");
  await check("UR-03", async () => {
    ensure(await page.getByRole("button", { name: "生成可核对的任务候选", exact: true }).count(), "draft action absent");
    ensure(!await page.getByRole("button", { name: /开始验收/ }).count(), "cold session contains task");
    return { coldSession: true, screenshot: await screen("cold") };
  });
  await check("UR-05", async () => {
    const input = page.locator('input[type="file"]').first();
    const invalid = [
      ["empty", ""], ["duplicate", '{"schema_version":"1.0","schema_version":"1.0"}'],
      ["float", '{"schema_version":"1.0","claimed_total_base_units":1.5,"claimed_count":0,"transfers":[]}'],
      ["missing", '{"schema_version":"1.0"}'],
      ["wrong-source", JSON.stringify({ ...config.reportData, transfers: config.reportData.transfers.map(row => ({...row, source: "rpc"})) })],
      ["count-limit", JSON.stringify({ ...config.reportData, transfers: Array(201).fill(config.reportData.transfers[0]) })],
      ["encoding", Buffer.from([255, 254, 253])],
      ["size-limit", " ".repeat(1048577)],
    ];
    const observed = [];
    for (const [name, text] of invalid) {
      await input.setInputFiles([]);
      await input.setInputFiles({ name: `${name}.json`, mimeType: "application/json", buffer: Buffer.from(text) });
      await page.getByText(name === "size-limit" ? /exceeds|too large|超过|1MB/ : /无法解析报表/).first().waitFor();
      if (name === "size-limit") { observed.push(name); continue; }
      ensure(await page.getByRole("button", { name: "生成可核对的任务候选", exact: true }).isDisabled(), "invalid upload can draft");
      observed.push(name);
    }
    await input.setInputFiles([]);
    await input.setInputFiles(config.report);
    await page.getByText(/已读取/).waitFor();
    ensure(await page.getByRole("button", { name: "生成可核对的任务候选", exact: true }).isEnabled(), "valid upload did not recover");
    return { rejected: observed, validRecovery: true, screenshot: await screen("upload-recovered") };
  });
  await check("UR-10", async () => {
    await page.getByText("查看上传格式与身份说明", { exact: true }).click();
    ensure(await page.getByText(/不表示外部作者/).isVisible(), "author caveat absent");
    return { authorUnverified: true, screenshot: await screen("identity") };
  });
  await check("UR-12", async () => {
    const sizes = [[1440,1000], [390,844], [759,900], [761,900], [720,500]];
    const measurements = [];
    for (const [width, height] of sizes) {
      await page.setViewportSize({ width, height });
      const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, inner: innerWidth }));
      ensure(dimensions.scroll <= dimensions.inner, `horizontal overflow at ${width}`);
      ensure(await page.getByRole("button", { name: "生成可核对的任务候选", exact: true }).isVisible(), "main action hidden");
      measurements.push({ width, height, ...dimensions, screenshot: await screen(`viewport-${width}`) });
    }
    return { measurements, coverage: "input screen only; 720px is not browser zoom" };
  });
  const responsive = results.find(item => item.id === "UR-12");
  if (responsive.status === "PASS") { responsive.status = "BLOCKED"; responsive.reason = "result views and actual 200% browser zoom require completion"; }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await check("UR-13", async () => {
    await page.getByRole("textbox", { name: "核验范围说明", exact: true }).focus();
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    ensure(focused === "TEXTAREA", "scope cannot receive focus");
    await page.keyboard.press("Tab");
    const next = await page.evaluate(() => ({ tag: document.activeElement?.tagName, text: document.activeElement?.textContent?.slice(0, 80) }));
    ensure(next.tag === "BUTTON", "scope tab navigation does not reach action");
    return { focused, next, screenshot: await screen("keyboard"), coverage: "input path only" };
  });
  const keyboard = results.find(item => item.id === "UR-13");
  if (keyboard.status === "PASS") { keyboard.status = "BLOCKED"; keyboard.reason = "result evidence and full keyboard path not executed"; }
  await check("UR-06", async () => {
    ensure(!await page.getByRole("button", { name: /开始验收/ }).count(), "execution visible before confirmation");
    return { executionAbsentBeforeConfirmation: true };
  });
  __M14_FLOW__
  return results;
}
