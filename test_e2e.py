# -*- coding: utf-8 -*-
import sys
import subprocess
import time

# Auto-install dependencies if missing
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("📢 [Playwright] 'playwright' library is not installed. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright

def run_test():
    target_url = "http://localhost:8081/index.html"
    print(f"🤖 [E2E Test] Connecting to {target_url} ...")
    
    errors = []
    
    with sync_playwright() as p:
        # Launch headless/headful browser
        # headful mode (headless=False) is excellent for visual verification
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        # 1. Listen for console errors
        def on_console_message(msg):
            if msg.type == "error":
                print(f"❌ [Console Error] {msg.text}")
                errors.append(msg.text)
            else:
                print(f"💬 [Console] {msg.text}")
                
        page.on("console", on_console_message)
        
        # Listen for uncaught exceptions
        page.on("pageerror", lambda err: errors.append(f"Uncaught Exception: {err.message}"))
        
        try:
            # 2. Open the page
            page.goto(target_url, timeout=30000)
            print("✅ [E2E Test] Page loaded successfully.")
            
            # Wait for any initialization if needed
            time.sleep(2)
            
            # 3. Handle initial landing screen mode selection if present
            # If the custom controls guide is displayed, click "start-seat-select-btn"
            seat_mode_btn = page.locator("#start-seat-select-btn")
            hud_trigger_btn = page.locator("#hud-seatmap-trigger")
            
            if seat_mode_btn.is_visible():
                print("➡️ [E2E Test] Clicking service select mode: Seat Selection...")
                seat_mode_btn.click()
            elif hud_trigger_btn.is_visible():
                print("➡️ [E2E Test] Clicking HUD seatmap trigger...")
                hud_trigger_btn.click()
            else:
                # If neither is immediately visible, check if we need to click play button or wait
                play_btn = page.locator("#play-button")
                if play_btn.is_visible():
                    print("➡️ [E2E Test] Click play-button to load Shapespark...")
                    play_btn.click()
                    time.sleep(2)
                
                # Check again for seat selector
                if seat_mode_btn.is_visible():
                    seat_mode_btn.click()
                elif hud_trigger_btn.is_visible():
                    hud_trigger_btn.click()
            
            time.sleep(2.5) # Wait for popup fade-in & SVG rendering
            
            # 4. Interact with the seatmap popup
            print("➡️ [E2E Test] Opening seatmap popup...")
            seatmap_popup = page.locator("#seatmap-popup")
            if not seatmap_popup.is_visible():
                # Try clicking HUD trigger if it wasn't opened
                if hud_trigger_btn.is_visible():
                    hud_trigger_btn.click()
                    time.sleep(1.5)
            
            # Check 1F - B Block section btn and click it
            b_block_btn = page.locator('.section-btn[data-floor="1F"][data-zone="B"]')
            if b_block_btn.is_visible():
                print("➡️ [E2E Test] Switching to 1F B-Block...")
                b_block_btn.click()
                time.sleep(1.5)
            
            # 5. Click a dynamic seat SVG element
            seats = page.locator('.seat-rect')
            seats_count = seats.count()
            print(f"📊 [E2E Test] Found {seats_count} seats on the current map.")
            
            if seats_count > 0:
                # Select a seat from the middle
                target_seat = seats.nth(seats_count // 2)
                seat_id = target_seat.get_attribute("data-seat-id") or target_seat.get_attribute("id")
                floor = target_seat.get_attribute("data-floor")
                zone = target_seat.get_attribute("data-zone")
                row = target_seat.get_attribute("data-row")
                seat_num = target_seat.get_attribute("data-number")
                
                print(f"➡️ [E2E Test] Clicking seat: [{floor} {zone}블록 {row}열 {seat_num}번] (ID: {seat_id})")
                
                # Force click since SVG rects sometimes need force dispatch in playwright
                target_seat.click(force=True)
                
                # Wait to let 3D transition and callbacks execute
                time.sleep(3)
                
                # Verify that selected seat text is updated in the trigger button or main UI
                btn_seatmap = page.locator("#btn_seatmap")
                if btn_seatmap.is_visible():
                    updated_text = btn_seatmap.inner_text()
                    print(f"🎯 [E2E Test] Main HUD text updated to: '{updated_text}'")
            else:
                print("⚠️ [E2E Test] No seats were interactable or rendered.")
            
        except Exception as e:
            print(f"❌ [E2E Test] Test flow threw an exception: {e}")
            errors.append(str(e))
        
        # Close the browser
        print("🤖 [E2E Test] Closing browser...")
        browser.close()

    # 6. Report test results
    print("\n" + "="*50)
    if errors:
        print("❌ [E2E Test Result] TEST FAILED! Captured Errors:")
        for err in errors:
            print(f"   - {err}")
        sys.exit(1)
    else:
        print("✅ [E2E Test Result] ALL TESTS PASSED! No console or execution errors detected.")
        sys.exit(0)

if __name__ == "__main__":
    run_test()
