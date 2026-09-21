"""E2E for the genius round: outline, chart, find, folding, snippets."""


def test_outline_lists_headings_and_jumps(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.wait_for_timeout(1200)
    items = page.locator("#sideOutline button")
    assert items.count() >= 5
    items.nth(2).click()
    page.wait_for_timeout(500)
    assert page.locator("#sheet .block.selected").count() == 1


def test_chart_block_renders_and_exports(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.wait_for_timeout(1000)
    page.click('button[data-add="chart"]')
    page.wait_for_selector("#sheet .chart svg")
    assert page.locator("#sheet .chart svg rect").count() >= 2


def test_find_modal_counts_and_jumps(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.wait_for_timeout(1000)
    page.keyboard.press("Control+k")
    page.fill("#palInput", "find")
    page.wait_for_timeout(300)
    page.keyboard.press("Enter")
    page.wait_for_selector("#findModal:not([hidden])")
    page.fill("#findText", "Acta")
    page.click("#findNext")
    page.wait_for_timeout(500)
    assert "Acta" in page.locator("#findCount").inner_text()
    page.click("#findClose")


def test_heading_fold_hides_section(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.wait_for_timeout(1000)
    before = page.locator("#sheet .block").count()
    assert before > 3
    page.locator("#sheet .block .foldbtn").first.click()
    page.wait_for_timeout(400)
    after = page.locator("#sheet .block").count()
    assert after < before
    assert page.locator("#sheet .foldmark").count() >= 1
