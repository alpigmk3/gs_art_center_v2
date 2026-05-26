(function () {
  // --- Global Zoom, Pan, Floor State ---
  let activeFloor = '1F';
  let activeZone = null;
  let scale = 1.0;
  let posX = 0;
  let posY = 0;
  let isDragging = false;
  let startX = 0, startY = 0;

  // --- View Configuration Overrides (Coordinate Offsets & Zoom Scale) ---
  // dx: Shift horizontal center (positive moves right, negative moves left)
  // dy: Shift vertical center (positive moves down, negative moves up)
  // scale: Manual zoom magnification factor

  // 1, 2, 3층 층별 설정 배열 (dx, dy는 동적 정렬 후 추가로 보정할 상대적 오프셋 값입니다)
  const SEATMAP_FLOOR_CONFIG = [
    { floor: '1F', dx: 0, dy: 100, scale: 1.95 },
    { floor: '2F', dx: 0, dy: -40, scale: 2.75 },
    { floor: '3F', dx: 0, dy: -110, scale: 2.75 }
  ];

  // 각 층의 A, B, C 구역별 설정 배열 (dx, dy는 동적 정렬 후 추가로 보정할 상대적 오프셋 값입니다)
  const SEATMAP_SECTION_CONFIG = [
    // 1층 구역 설정 (A, B, C) - 무대쪽이 더 보이도록 dy 오프셋 설정
    { floor: '1F', zone: 'A', dx: 0, dy: 120, scale: 2.8 },
    { floor: '1F', zone: 'B', dx: 0, dy: 120, scale: 2.8 },
    { floor: '1F', zone: 'C', dx: 0, dy: 120, scale: 2.8 },

    // 2층 구역 설정 (A, B, C) - 가로축 고정 및 세로축 움직임 구분을 위해 dy 조정 (-30)
    { floor: '2F', zone: 'A', dx: 0, dy: -30, scale: 4.0 },
    { floor: '2F', zone: 'B', dx: 0, dy: -30, scale: 4.0 },
    { floor: '2F', zone: 'C', dx: 0, dy: -30, scale: 4.0 },

    // 3층 구역 설정 (A, B, C) - 가로축 고정 및 세로축 움직임 구분을 위해 dy 조정 (-110)
    { floor: '3F', zone: 'A', dx: 0, dy: -110, scale: 3.4 },
    { floor: '3F', zone: 'B', dx: 0, dy: -110, scale: 3.4 },
    { floor: '3F', zone: 'C', dx: 0, dy: -110, scale: 3.4 }
  ];

  // --- Helper: Attach Robust Loading & Auto-Click Hooks to Shapespark ---
  function initShapesparkLoader() {
    const playButton = document.getElementById('play-button');
    const secondaryProgress = document.getElementById('secondary-progress');
    const secondaryProgressDone = document.getElementById('secondary-progress-done');
    const customProgressBar = document.getElementById('custom-progress-bar');
    const customProgressText = document.getElementById('custom-progress-text');
    const customLoadingScreen = document.getElementById('custom-loading-screen');
    const controlsGuideScreen = document.getElementById('controls-guide-screen');

    let clickInterval = null;
    let progressInterval = null;
    let loadCompleted = false;

    console.log("Initializing premium Shapespark loader...");

    // 1. Programmatically trigger play-button to start asset downloads
    clickInterval = setInterval(() => {
      if (loadCompleted) {
        clearInterval(clickInterval);
        return;
      }

      if (playButton && playButton.style.display !== 'none') {
        console.log("Shapespark play-button is active in DOM. Triggering click programmatically...");
        playButton.click();

        // Check if loading has actually begun
        const currentWidth = secondaryProgressDone ? secondaryProgressDone.style.width : '';
        if (currentWidth && currentWidth !== '0%' && currentWidth !== '') {
          console.log("Asset downloading active. Stopping click loop.");
          clearInterval(clickInterval);
        }
      }
    }, 100);

    // 2. Poll loading progress from native secondary-progress-done width
    progressInterval = setInterval(() => {
      if (loadCompleted) {
        clearInterval(progressInterval);
        return;
      }

      let progressPercent = 0;
      if (secondaryProgressDone) {
        const widthStr = secondaryProgressDone.style.width;
        if (widthStr) {
          const parsed = parseFloat(widthStr);
          if (!isNaN(parsed)) {
            progressPercent = Math.round(parsed);
          }
        }
      }

      // Update custom loading UI
      if (customProgressBar) {
        customProgressBar.style.width = progressPercent + '%';
      }
      if (customProgressText) {
        customProgressText.innerText = progressPercent + '%';
      }

      // Complete conditions: width is 100% or shapespark hides the native loading bar
      const isNativeHidden = secondaryProgress && secondaryProgress.style.display === 'none';

      if (progressPercent >= 100 || (progressPercent > 10 && isNativeHidden)) {
        console.log("Shapespark loading sequence complete!");
        loadCompleted = true;
        clearInterval(clickInterval);
        clearInterval(progressInterval);

        if (customProgressBar) customProgressBar.style.width = '100%';
        if (customProgressText) customProgressText.innerText = '100%';

        // Transition out loader, show guide modal
        setTimeout(() => {
          if (customLoadingScreen) {
            customLoadingScreen.style.opacity = '0';
            setTimeout(() => {
              customLoadingScreen.style.display = 'none';
              if (controlsGuideScreen) {
                controlsGuideScreen.style.display = 'flex';
                controlsGuideScreen.style.opacity = '1';
              }
            }, 500);
          }
        }, 400);
      }
    }, 50);
  }

  // --- Helper: Interface Event Handlers ---
  function setupUIEventHandlers() {
    const guideScreen = document.getElementById('controls-guide-screen');
    const mainHUD = document.getElementById('walkthrough-hud');
    const seatmapPopup = document.getElementById('seatmap-popup');

    // Mode Selection Handlers
    document.getElementById('start-free-move-btn').addEventListener('click', () => {
      guideScreen.style.opacity = '0';
      setTimeout(() => {
        guideScreen.style.display = 'none';
        mainHUD.style.display = 'block';
        mainHUD.style.opacity = '1';
      }, 300);
    });

    document.getElementById('start-auto-tour-btn').addEventListener('click', () => {
      guideScreen.style.opacity = '0';
      setTimeout(() => {
        guideScreen.style.display = 'none';
        mainHUD.style.display = 'block';
        mainHUD.style.opacity = '1';

        // Trigger auto tour
        const viewer = WALK.getViewer();
        if (viewer) viewer.playTour();
      }, 300);
    });

    document.getElementById('start-seat-select-btn').addEventListener('click', () => {
      guideScreen.style.opacity = '0';
      setTimeout(() => {
        guideScreen.style.display = 'none';
        mainHUD.style.display = 'block';
        mainHUD.style.opacity = '1';

        // Trigger seatmap display immediately
        openSeatmapPopup();
      }, 300);
    });

    // Main HUD Triggers
    document.getElementById('hud-seatmap-trigger').addEventListener('click', openSeatmapPopup);

    document.getElementById('hud-stage-trigger').addEventListener('click', () => {
      const isEng = window.location.pathname.includes('_eng.html');
      if (isEng) {
        alert("Stage change API placeholder. (Feature coming soon)");
      } else {
        alert("무대 변경 API 호출 공간입니다. (기능 준비중)");
      }
    });

    // Seatmap Modal Controls
    document.getElementById('seatmap-close-btn').addEventListener('click', closeSeatmapPopup);

    document.getElementById('seatmap-lang-toggle').addEventListener('click', () => {
      const isEng = window.location.pathname.includes('_eng.html');
      window.location.href = isEng ? 'index.html' : 'index_eng.html';
    });

    // Overlay Click: Close when clicking empty space outside the popup card
    seatmapPopup.addEventListener('click', (e) => {
      const card = seatmapPopup.querySelector('.seatmap-popup-card');
      if (card && !card.contains(e.target)) {
        closeSeatmapPopup();
      }
    });

    // Floor Selector Buttons Click Listeners
    document.querySelectorAll('.floor-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const floor = btn.getAttribute('data-floor');
        centerOnFloor(floor);
      });
    });

    // Section Selector Buttons Click Listeners
    document.querySelectorAll('.section-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const floor = btn.getAttribute('data-floor');
        const zone = btn.getAttribute('data-zone');
        centerOnSection(floor, zone);
      });
    });

    // Zoom Buttons
    document.getElementById('zoom-in-btn').addEventListener('click', zoomIn);
    document.getElementById('zoom-out-btn').addEventListener('click', zoomOut);
    document.getElementById('zoom-reset-btn').addEventListener('click', resetZoom);

    // Responsive window resize event listener to automatically re-center active floor or section
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        const overlay = document.getElementById('seatmap-popup');
        // Only trigger re-centering if the seatmap modal is currently open and active
        if (overlay && overlay.classList.contains('active')) {
          if (activeZone) {
            centerOnSection(activeFloor, activeZone);
          } else {
            centerOnFloor(activeFloor);
          }
        }
      }, 150);
    });
  }

  // --- Helper: Zoom and Pan Functionality ---
  function initZoomPanControls() {
    const viewport = document.querySelector('.seatmap-zoom-viewport');

    // Desktop Drag Pan
    viewport.addEventListener('mousedown', (e) => {
      if (e.target.closest('.zoom-controls') || e.target.closest('.seatmap-floor-selector') || e.target.closest('.seatmap-section-selector')) return;
      isDragging = true;
      viewport.style.cursor = 'grabbing';
      startX = e.clientX - posX;
      startY = e.clientY - posY;
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
      viewport.style.cursor = 'grab';
    });

    viewport.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      posX = e.clientX - startX;
      posY = e.clientY - startY;
      applyTransform();
    });

    // Mobile Touch Pan
    viewport.addEventListener('touchstart', (e) => {
      if (e.target.closest('.zoom-controls') || e.target.closest('.seatmap-floor-selector') || e.target.closest('.seatmap-section-selector')) return;
      if (e.touches.length === 1) {
        isDragging = true;
        startX = e.touches[0].clientX - posX;
        startY = e.touches[0].clientY - posY;
      }
    });

    viewport.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      if (e.touches.length === 1) {
        posX = e.touches[0].clientX - startX;
        posY = e.touches[0].clientY - startY;
        applyTransform();
      }
    });

    viewport.addEventListener('touchend', () => {
      isDragging = false;
    });

    // Mouse Wheel Zoom
    viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      if (e.deltaY < 0) {
        zoomIn();
      } else {
        zoomOut();
      }
    });
  }

  function zoomToScale(newScale) {
    const viewport = document.querySelector('.seatmap-zoom-viewport');
    if (!viewport) return;
    const viewWidth = viewport.clientWidth;
    const viewHeight = viewport.clientHeight;
    const cx = viewWidth / 2;
    const cy = viewHeight / 2;

    newScale = Math.max(0.5, Math.min(newScale, 4.0));

    // Pan relative to center of viewport
    posX = cx - (cx - posX) * (newScale / scale);
    posY = cy - (cy - posY) * (newScale / scale);
    scale = newScale;

    applyTransform();
  }

  // Define zoom controls
  function zoomIn() {
    zoomToScale(scale + 0.2);
  }

  function zoomOut() {
    zoomToScale(scale - 0.2);
  }

  function resetZoom() {
    centerOnFloor(activeFloor);
  }

  function applyTransform() {
    const content = document.getElementById('seatmap-zoom-content');
    if (content) {
      content.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
      content.style.transition = isDragging ? 'none' : 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
    }
  }

  // --- Helper: Dynamic Bounding Box Centering Logic ---
  function centerOnSVGArea(filterFn, defaultScale, viewConfig) {
    const viewport = document.querySelector('.seatmap-zoom-viewport');
    const content = document.getElementById('seatmap-zoom-content');
    const svgEl = content.querySelector('svg');
    if (!viewport || !content || !svgEl) return;

    const config = viewConfig || { dx: 0, dy: 0, scale: defaultScale };

    // Calculate bounding box of filtered elements in SVG local space
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    let found = false;

    const rects = svgEl.querySelectorAll('rect');
    rects.forEach(rect => {
      if (filterFn(rect)) {
        const bbox = rect.getBBox();
        if (bbox.width > 0 && bbox.height > 0) {
          minX = Math.min(minX, bbox.x);
          minY = Math.min(minY, bbox.y);
          maxX = Math.max(maxX, bbox.x + bbox.width);
          maxY = Math.max(maxY, bbox.y + bbox.height);
          found = true;
        }
      }
    });

    if (!found) {
      console.warn("No matching elements found to center on.");
      return;
    }

    // Target center in SVG local space
    const targetX = (minX + maxX) / 2;
    const targetY = (minY + maxY) / 2;

    // Viewport dimensions
    const viewWidth = viewport.clientWidth;
    const viewHeight = viewport.clientHeight;

    // SVG viewBox attributes
    const viewBox = svgEl.viewBox.baseVal || { width: 701, height: 1232 };
    const viewBoxWidth = viewBox.width;
    const viewBoxHeight = viewBox.height;

    // Calculate renderScale and offsets
    const renderScale = Math.min(viewWidth / viewBoxWidth, viewHeight / viewBoxHeight);

    let offsetX = 0;
    let offsetY = 0;
    if (viewWidth / viewBoxWidth > viewHeight / viewBoxHeight) {
      offsetX = (viewWidth - viewBoxWidth * renderScale) / 2;
    } else {
      offsetY = (viewHeight - viewBoxHeight * renderScale) / 2;
    }

    // Calculate container scale point
    const px = targetX * renderScale + offsetX;
    const py = targetY * renderScale + offsetY;

    scale = config.scale || defaultScale || 1.0;
    posX = viewWidth / 2 - px * scale + (config.dx || 0);
    posY = viewHeight / 2 - py * scale + (config.dy || 0);

    applyTransform();
  }

  function centerOnFloor(floorCode) {
    activeFloor = floorCode;
    activeZone = null;

    // Update Floor Selector UI buttons active state
    document.querySelectorAll('.floor-btn').forEach(btn => {
      if (btn.getAttribute('data-floor') === floorCode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Reset Section Selector active buttons
    document.querySelectorAll('.section-btn').forEach(btn => btn.classList.remove('active'));

    const config = SEATMAP_FLOOR_CONFIG.find(item => item.floor === floorCode);

    let filterFn;
    if (floorCode === '1F') {
      filterFn = rect => {
        const y = parseFloat(rect.getAttribute('y')) || 0;
        const bbox = rect.getBBox();
        return y < 600 && bbox.width > 0 && bbox.width < 50 && !rect.closest('defs');
      };
    } else if (floorCode === '2F') {
      filterFn = rect => {
        const y = parseFloat(rect.getAttribute('y')) || 0;
        const bbox = rect.getBBox();
        return y >= 600 && y < 950 && bbox.width > 0 && bbox.width < 50 && !rect.closest('defs');
      };
    } else { // '3F'
      filterFn = rect => {
        const y = parseFloat(rect.getAttribute('y')) || 0;
        const bbox = rect.getBBox();
        return y >= 950 && bbox.width > 0 && bbox.width < 50 && !rect.closest('defs');
      };
    }

    centerOnSVGArea(filterFn, 1.15, config);
  }

  function centerOnSectionSVGArea(floorCode, zoneCode, defaultScale, viewConfig) {
    const viewport = document.querySelector('.seatmap-zoom-viewport');
    const content = document.getElementById('seatmap-zoom-content');
    const svgEl = content.querySelector('svg');
    if (!viewport || !content || !svgEl) return;

    const config = viewConfig || { dx: 0, dy: 0, scale: defaultScale };

    let zoneMinX = Infinity, zoneMaxX = -Infinity;
    let zoneFound = false;

    let floorMinY = Infinity, floorMaxY = -Infinity;
    let floorFound = false;

    const rects = svgEl.querySelectorAll('rect');
    rects.forEach(rect => {
      const y = parseFloat(rect.getAttribute('y')) || 0;
      const bbox = rect.getBBox();
      const isDefs = rect.closest('defs');
      if (bbox.width <= 0 || bbox.width >= 50 || isDefs) return;

      let matchFloor = false;
      if (floorCode === '1F') matchFloor = y < 600;
      else if (floorCode === '2F') matchFloor = y >= 600 && y < 950;
      else matchFloor = y >= 950;

      if (matchFloor) {
        floorMinY = Math.min(floorMinY, bbox.y);
        floorMaxY = Math.max(floorMaxY, bbox.y + bbox.height);
        floorFound = true;

        let matchZone = false;
        if (zoneCode === 'A') matchZone = bbox.x < 280;
        else if (zoneCode === 'B') matchZone = bbox.x >= 280 && bbox.x <= 420;
        else matchZone = bbox.x > 420;

        if (matchZone) {
          zoneMinX = Math.min(zoneMinX, bbox.x);
          zoneMaxX = Math.max(zoneMaxX, bbox.x + bbox.width);
          zoneFound = true;
        }
      }
    });

    if (!zoneFound || !floorFound) {
      console.warn("No matching elements found for section centering.");
      return;
    }

    const targetX = (zoneMinX + zoneMaxX) / 2;
    const targetY = (floorMinY + floorMaxY) / 2;

    const viewWidth = viewport.clientWidth;
    const viewHeight = viewport.clientHeight;

    const viewBox = svgEl.viewBox.baseVal || { width: 701, height: 1232 };
    const viewBoxWidth = viewBox.width;
    const viewBoxHeight = viewBox.height;

    const renderScale = Math.min(viewWidth / viewBoxWidth, viewHeight / viewBoxHeight);

    let offsetX = 0;
    let offsetY = 0;
    if (viewWidth / viewBoxWidth > viewHeight / viewBoxHeight) {
      offsetX = (viewWidth - viewBoxWidth * renderScale) / 2;
    } else {
      offsetY = (viewHeight - viewBoxHeight * renderScale) / 2;
    }

    const px = targetX * renderScale + offsetX;
    const py = targetY * renderScale + offsetY;

    scale = config.scale || defaultScale || 1.0;
    posX = viewWidth / 2 - px * scale + (config.dx || 0);
    posY = viewHeight / 2 - py * scale + (config.dy || 0);

    applyTransform();
  }

  function centerOnSection(floorCode, zoneCode) {
    activeFloor = floorCode;
    activeZone = zoneCode;

    // Update Floor Selector UI active state
    document.querySelectorAll('.floor-btn').forEach(btn => {
      if (btn.getAttribute('data-floor') === floorCode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update Section Selector UI buttons active state
    document.querySelectorAll('.section-btn').forEach(btn => {
      const f = btn.getAttribute('data-floor');
      const z = btn.getAttribute('data-zone');
      if (f === floorCode && z === zoneCode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const config = SEATMAP_SECTION_CONFIG.find(item => item.floor === floorCode && item.zone === zoneCode);
    centerOnSectionSVGArea(floorCode, zoneCode, 2.2, config);
  }

  // --- Helper: Dynamic SVG Loader & Seat Event Delegation ---
  function openSeatmapPopup() {
    const overlay = document.getElementById('seatmap-popup');
    const card = overlay.querySelector('.seatmap-popup-card');

    overlay.style.display = 'flex';
    overlay.offsetHeight;

    overlay.classList.add('active');
    card.classList.add('active');

    loadSeatmapSVG();
  }

  function loadSeatmapSVG() {
    const content = document.getElementById('seatmap-zoom-content');
    if (!content) return;

    if (content.children.length === 0) {
      const isEng = window.location.pathname.includes('_eng.html');
      content.innerHTML = isEng
        ? '<div style="color:#121212;text-align:center;padding-top:20vh;font-weight:600;">Loading seat map...</div>'
        : '<div style="color:#121212;text-align:center;padding-top:20vh;font-weight:600;">배치도 파일 로드 중...</div>';

      const svgFile = isEng ? 'seatmap_eng.svg' : 'seatmap_kor.svg';

      fetch(svgFile)
        .then(res => {
          if (!res.ok) throw new Error('SVG fetch failed');
          return res.text();
        })
        .then(svgText => {
          content.innerHTML = svgText;

          // Bind interactive click handlers to newly added seats and tag metadata attributes
          setupSeatClickEvents();

          // Initialize zoom transform and drag interactions
          initZoomPanControls();

          // Center on active floor initially
          setTimeout(() => {
            centerOnFloor(activeFloor);
          }, 100);
        })
        .catch(err => {
          console.error(err);
          const isEng = window.location.pathname.includes('_eng.html');
          content.innerHTML = `<div style="color:#ff6b6b;text-align:center;padding-top:20vh;font-weight:600;">${isEng ? 'Failed to load seatmap file.' : '배치도 파일을 불러오지 못했습니다.'}</div>`;
        });
    } else {
      setTimeout(() => {
        centerOnFloor(activeFloor);
      }, 100);
    }
  }

  function closeSeatmapPopup() {
    const overlay = document.getElementById('seatmap-popup');
    const card = overlay.querySelector('.seatmap-popup-card');

    overlay.classList.remove('active');
    card.classList.remove('active');

    setTimeout(() => {
      if (!overlay.classList.contains('active')) {
        overlay.style.display = 'none';
      }
    }, 500);
  }

  function setupSeatClickEvents() {
    const svg = document.querySelector('#seatmap-zoom-content svg');
    if (!svg) return;

    const rects = svg.querySelectorAll('rect');
    const seatMapLookup = {};
    if (typeof GS_ARTS_CENTER_SEAT_MAP_DATA !== 'undefined') {
      GS_ARTS_CENTER_SEAT_MAP_DATA.forEach(s => { seatMapLookup[s.View_ID] = s; });
    }

    rects.forEach((rect) => {
      rect.classList.add('seat-rect');
      const id = rect.getAttribute('id');
      const seatData = seatMapLookup[id];

      if (seatData) {
        rect.setAttribute('data-floor', seatData.Floor);
        rect.setAttribute('data-zone', seatData.Zone);
        rect.setAttribute('data-row', seatData.Row);
        rect.setAttribute('data-number', seatData.Seat_Number);
        rect.setAttribute('data-view-id', seatData.View_ID);
        rect.setAttribute('data-seat-id', id);

        rect.addEventListener('click', () => {
          document.querySelectorAll('.seat-rect.active').forEach(el => el.classList.remove('active'));
          rect.classList.add('active');

          const viewer = WALK.getViewer();
          if (!viewer) return;

          const view = new WALK.View();
          view.position.x = seatData.X;
          view.position.y = seatData.Y;
          view.position.z = seatData.Z;

          const vec_LookAt = new THREE.Vector3(18.22, 12.4, 4.5);
          const m = new THREE.Matrix4();
          m.lookAt(view.position, vec_LookAt, new THREE.Vector3(0, 0, 1));
          let ves = new THREE.Euler();
          ves.setFromRotationMatrix(m, 'ZYX');

          view.rotation.z = ves.z;
          viewer.switchToView(view);

          const floorText = seatData.Floor.replace('F', '층');
          const displayText = `${floorText} ${seatData.Zone}블록 ${seatData.Row} ${seatData.Seat_Number}좌석`;
          const btn_seatmap = document.getElementById('btn_seatmap');
          if (btn_seatmap) {
            btn_seatmap.innerText = displayText;
          }

          setTimeout(() => {
            closeSeatmapPopup();
          }, 400);
        });
      } else {
        // ID 없는 rect (배경 장식 등) — 클릭 이벤트 미등록
        if (id) console.warn(`No seat metadata for ID: ${id}`);
      }
    });
  }

  // --- Automated Self-Test Helper ---
  window.runAutomaticSeatmapTest = function() {
    console.log("🤖 [Auto-Test] Starting automatic seatmap test...");
    
    const triggerBtn = document.getElementById('hud-seatmap-trigger') || document.getElementById('start-seat-select-btn');
    if (!triggerBtn) {
      console.error("❌ [Auto-Test] Seatmap trigger button not found.");
      return;
    }
    console.log("➡️ [Auto-Test] Clicking seatmap trigger button...");
    triggerBtn.click();
    
    setTimeout(() => {
      const sectionBtn = document.querySelector('.section-btn[data-floor="1F"][data-zone="B"]');
      if (!sectionBtn) {
        console.error("❌ [Auto-Test] Section button (1F - B block) not found.");
        return;
      }
      console.log("➡️ [Auto-Test] Switching to 1F B-Block...");
      sectionBtn.click();
      
      setTimeout(() => {
        const seats = document.querySelectorAll('.seat-rect');
        if (seats.length === 0) {
          console.error("❌ [Auto-Test] No seats found on the SVG map.");
          return;
        }
        
        const targetSeatIndex = Math.floor(seats.length / 2);
        const targetSeat = seats[targetSeatIndex];
        const seatId = targetSeat.getAttribute('data-seat-id') || targetSeat.id;
        const floor = targetSeat.getAttribute('data-floor');
        const zone = targetSeat.getAttribute('data-zone');
        const row = targetSeat.getAttribute('data-row');
        const seatNum = targetSeat.getAttribute('data-number');
        
        console.log(`➡️ [Auto-Test] Clicking target seat [${floor} ${zone}블록 ${row}열 ${seatNum}번] (ID: ${seatId})...`);
        
        let errorOccurred = false;
        const errorHandler = function(event) {
          console.error("❌ [Auto-Test] Uncaught exception detected during click:", event.error);
          errorOccurred = true;
        };
        window.addEventListener('error', errorHandler);
        
        try {
          targetSeat.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        } catch (e) {
          console.error("❌ [Auto-Test] Click handler threw synchronous error:", e);
          errorOccurred = true;
        }
        
        setTimeout(() => {
          window.removeEventListener('error', errorHandler);
          if (errorOccurred) {
            console.error("❌ [Auto-Test] Test Failed! Console errors were captured.");
          } else {
            console.log("✅ [Auto-Test] Test Passed! Click dispatched successfully without exceptions. Check 3D view changes.");
          }
        }, 1000);
        
      }, 1000);
    }, 500);
  };

  // --- Initialize App ---
  setupUIEventHandlers();
  initShapesparkLoader();
})();
