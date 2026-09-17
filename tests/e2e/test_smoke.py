"""Browser smoke: create -> edit -> export -> library round-trip."""


def test_home_loads_editor(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet")
    assert "gen-pdf" in page.title().lower()
    assert page.locator(".block").count() > 0  # acta template preloaded


def test_add_paragraph_and_export_pdf(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.click('button[data-add="paragraph"]')
    page.locator(".block.selected .redit").click()
    page.locator(".block.selected .editable").fill("Hello e2e **world**")
    page.keyboard.press("Escape")
    with page.expect_download() as dl:
        page.click("#btnPdf")
    download = dl.value
    assert download.suggested_filename.endswith(".pdf")
    path = download.path()
    assert path.stat().st_size > 2000


def test_slash_menu_inserts_table(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.locator(".block .redit").first.click()
    page.wait_for_selector(".block .editable")
    page.keyboard.press("End")
    page.keyboard.type("/tab", delay=40)
    page.wait_for_selector("#floatMenu:not([hidden])")
    assert "table" in page.locator("#floatMenu").inner_text().lower()
    page.keyboard.press("Enter")
    page.wait_for_selector("table.ed")


def test_save_and_reopen_from_library(page, server):
    page.goto(server + "/")
    page.wait_for_selector("#sheet .block")
    page.click("#btnSave")
    page.wait_for_selector(".toast")
    page.click('#sidebar [data-view="library"]')
    page.wait_for_selector(".libCard")
    assert page.locator(".libCard").count() >= 1
    page.locator(".libCard button").first.click()
    page.wait_for_selector("#sheet .block")
    assert page.locator("#viewEditor").is_visible()
