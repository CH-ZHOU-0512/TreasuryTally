  // Included inside the driver function; all actions use the actual page.
  await check("UR-02", async () => {
    const uploader = page.locator('input[type="file"]').first();
    await uploader.setInputFiles(config.report);
    await page.getByText(/已读取/).waitFor();
    await page.getByRole("textbox", { name: "核验范围说明", exact: true }).fill(config.scope);
    await page.getByRole("button", { name: "生成可核对的任务候选", exact: true }).click();
    await page.getByRole("button", { name: "确认并冻结 TaskSpec", exact: true }).waitFor({ timeout: 90000 });
    await page.getByRole("spinbutton", { name: "Chain ID", exact: true }).fill(String(config.task.chain_id));
    await page.getByRole("textbox", { name: "代币地址", exact: true }).fill(config.task.token_address);
    await page.getByRole("spinbutton", { name: "起始区块（含）", exact: true }).fill(String(config.task.start_block));
    await page.getByRole("spinbutton", { name: "结束区块（含）", exact: true }).fill(String(config.task.end_block));
    await page.getByRole("textbox", { name: "资金账户（每行一个，最多两个）", exact: true }).fill(config.task.treasury_addresses.join("\n"));
    await page.getByRole("textbox", { name: "资助对象（每行一个）", exact: true }).fill(config.task.recipient_addresses.join("\n"));
    await page.getByRole("checkbox", { name: "排除资金账户之间的内部互转", exact: true }).setChecked(config.task.exclusion_rules.length > 0);
    await page.getByRole("button", { name: "确认并冻结 TaskSpec", exact: true }).click();
    await page.getByText("任务未确认：请先勾选任务边界确认框。", { exact: true }).waitFor();
    ensure(!await page.getByRole("button", { name: /开始验收/ }).count(), "unconfirmed task executed");
    const prior = results.find(item => item.id === "UR-06");
    prior.evidence.uncheckedConfirmationRejected = true;
    await page.getByRole("checkbox", { name: "我已核对链、资产、账户与区块边界，并确认冻结此任务", exact: true }).check();
    await page.getByRole("button", { name: "确认并冻结 TaskSpec", exact: true }).click();
    await page.getByRole("button", { name: "开始验收 · Attempt 1", exact: true }).waitFor();
    await page.getByRole("button", { name: "开始验收 · Attempt 1", exact: true }).click();
    await page.getByText(/验收通过/).first().waitFor({ timeout: 180000 });
    ensure((await page.locator("body").innerText()).includes(config.expectedTotal), "independent expected amount absent");
    await page.getByText("证据来源与采样诊断", { exact: true }).first().click();
    ensure((await page.locator("body").innerText()).includes("COMPLETE"), "real RPC completeness absent");
    await page.getByText("查看不可变任务指纹与完整边界", { exact: true }).click();
    const hash = await page.locator('code').filter({ hasText: /^0x[a-f0-9]{64}$/ }).first().innerText();
    return { expectedTotal: config.expectedTotal, taskHash: hash, realRpcComplete: true, screenshot: await screen("independent-pass") };
  });
  const independent = results.find(item => item.id === "UR-02");
  const cold = results.find(item => item.id === "UR-03");
  if (independent.status === "PASS" && cold.status === "PASS") cold.evidence.independentInputCompleted = true;
  else if (cold.status === "PASS") { cold.status = "BLOCKED"; cold.reason = "cold screen verified but independent path incomplete"; }
  if (independent.status === "PASS") {
    await check("UR-11", async () => {
      await page.getByText("公共回执与 ERC-8004", { exact: true }).first().click();
      const body = await page.locator("body").innerText();
      ensure(body.includes("NOT_SUBMITTED"), "publication state absent");
      const write = page.getByRole("button", { name: "发布公开 JSON 回执", exact: true });
      if (await write.count()) ensure(await write.isDisabled(), "unauthorized publish enabled");
      return { state: "NOT_SUBMITTED", clickedWrite: false, screenshot: await screen("write-isolation") };
    });
    await check("UR-04", async () => {
      await page.reload();
      await page.getByText("运行配置", { exact: true }).waitFor();
      await page.getByText("运行配置", { exact: true }).click();
      await page.getByRole("textbox", { name: "工作区 ID", exact: true }).fill(config.workspace);
      await page.getByRole("textbox", { name: "工作区 ID", exact: true }).press("Enter");
      await page.getByText(/验收通过/).first().waitFor({ timeout: 45000 });
      await page.getByText("查看不可变任务指纹与完整边界", { exact: true }).click();
      const restoredHash = await page.locator('code').filter({ hasText: /^0x[a-f0-9]{64}$/ }).first().innerText();
      ensure(restoredHash === independent.evidence.taskHash, "restored task fingerprint changed");
      return { restoredHash, screenshot: await screen("restored"), coverage: "page reload only; process/new-context restore pending" };
    });
    const restore = results.find(item => item.id === "UR-04");
    if (restore.status === "PASS") { restore.status = "BLOCKED"; restore.reason = "application process restart not executed"; }
  }
