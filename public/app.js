// --- Three.js Background Setup ---
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
// ⚡ Bolt Optimization: Disable WebGL antialiasing for particle systems.
// The scene only contains THREE.Points, which are drawn using gl.POINTS and do not benefit from MSAA.
// Disabling antialiasing avoids allocating a multisampled render buffer and executing expensive resolve passes
// on every frame, significantly reducing GPU memory and processing overhead with zero visual difference.
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: false });

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('three-canvas').appendChild(renderer.domElement);

const geometry = new THREE.BufferGeometry();
// ⚡ Bolt Optimization: Pre-allocate a Float32Array instead of dynamically pushing to a standard JS array.
// This prevents dynamic memory reallocation and significantly reduces garbage collection overhead during initialization.
const particleCount = 5000;
const vertices = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount; i++) {
    vertices[i * 3] = THREE.MathUtils.randFloatSpread(2000);
    vertices[i * 3 + 1] = THREE.MathUtils.randFloatSpread(2000);
    vertices[i * 3 + 2] = THREE.MathUtils.randFloatSpread(2000);
}
geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
// ⚡ Bolt Optimization: Disable depth buffer writes for transparent particle systems.
// Writing to the depth buffer for semi-transparent particles is unnecessary (since they don't occlude each other strictly)
// and forces the GPU to perform thousands of redundant fragment operations. Setting depthWrite to false
// significantly reduces rendering overhead, especially on integrated GPUs.
const material = new THREE.PointsMaterial({ color: 0x4a90e2, size: 2, transparent: true, opacity: 0.5, depthWrite: false });
const particles = new THREE.Points(geometry, material);
scene.add(particles);

camera.position.z = 1000;

let animationFrameId;

// ⚡ Bolt Optimization: Pause WebGL render loop for static scenes
// If the user prefers reduced motion, the scene does not animate. Continuously calling
// requestAnimationFrame and renderer.render for a completely static scene wastes
// significant CPU and GPU resources (rendering 60 identical frames per second).
// We pause the loop entirely and only re-render once on static initializations or resize events.
function animate() {
    if (!prefersReducedMotion.matches) {
        particles.rotation.x += 0.0001;
        particles.rotation.y += 0.0002;
        renderer.render(scene, camera);
        animationFrameId = requestAnimationFrame(animate);
    } else {
        // Render exactly once if static
        renderer.render(scene, camera);
    }
}

// Start loop
animate();

// Listen for dynamic changes to the accessibility preference
prefersReducedMotion.addEventListener('change', (e) => {
    if (!e.matches) {
        // Motion is now allowed, restart loop
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        animate();
    } else {
        // Motion is disabled, stop loop
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    }
});

// ⚡ Bolt Optimization: Debounce WebGL resize events
// When performing heavy canvas or WebGL recalculations (like updateProjectionMatrix and renderer.setSize)
// in response to window resizing, debouncing prevents severe performance degradation and layout thrashing.
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);

        // ⚡ Bolt Optimization: Force a re-render if the loop is paused
        if (prefersReducedMotion.matches) {
            renderer.render(scene, camera);
        }
    }, 200);
});

// --- API Interaction & Chart Rendering ---

const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:8000/api' : '/api';

// ⚡ Bolt Optimization: Cache expensive API call results to eliminate network latency
// and prevent redundant backend processing for identical deterministic mathematical requests.
const apiCache = new Map();

async function fetchWithCache(endpoint, payload) {
    const cacheKey = `${endpoint}|${JSON.stringify(payload)}`;
    if (apiCache.has(cacheKey)) {
        return apiCache.get(cacheKey);
    }

    // 🛡️ Sentinel Security Enhancement: Add a timeout to prevent client-side hanging
    // and resource exhaustion if the backend becomes unresponsive or under DoS.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) await handleApiError(response);
        const data = await response.json();
        apiCache.set(cacheKey, data);
        return data;
    } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
            const timeoutErr = new Error("Request timed out. The server might be under heavy load.");
            timeoutErr.name = "ValidationError";
            throw timeoutErr;
        }
        throw err;
    }
}

async function handleApiError(response) {
    const text = await response.text();
    let errMsg = text;
    try {
        const errorData = JSON.parse(text);
        if (errorData.detail && Array.isArray(errorData.detail)) {
            // FastAPI/Pydantic validation error
            const messages = errorData.detail.map(err => {
                const loc = err.loc ? err.loc.join('.') : '';
                return `${loc ? `[${loc}] ` : ''}${err.msg}`;
            });
            errMsg = messages.join(', ');
        } else if (errorData.detail) {
            errMsg = errorData.detail;
        }
    } catch (e) {
        // Fallback to text string
    }
    const err = new Error(errMsg);
    err.name = "ValidationError";
    throw err;
}


// Utility to parse JSON array strings safely
function parseInput(id) {
    const el = document.getElementById(id);
    try {
        const parsed = JSON.parse(el.value);
        if (el.dataset.format === 'json' && !Array.isArray(parsed)) {
            throw new Error('Must be a JSON array');
        }
        el.setAttribute('aria-invalid', 'false');
        return parsed;
    } catch (e) {
        el.setCustomValidity('Invalid format. Please use valid JSON array format, e.g., [1, 0] or [[1,0],[0,1]]');
        el.setAttribute('aria-invalid', 'true');
        el.disabled = false;
        el.reportValidity();
        el.focus();
        const err = new Error('InputValidationError');
        err.name = 'InputValidationError';
        throw err;
    }
}

function parseFloatInput(id) {
    const el = document.getElementById(id);
    const val = parseFloat(el.value);
    if (isNaN(val)) {
        el.setCustomValidity('Please enter a valid number.');
        el.setAttribute('aria-invalid', 'true');
        el.disabled = false;
        el.reportValidity();
        el.focus();
        const err = new Error(`Invalid number in ${id}`);
        err.name = 'InputValidationError';
        throw err;
    }
    el.setAttribute('aria-invalid', 'false');
    return val;
}

// ⚡ Palette: Add real-time inline validation for JSON inputs on focusout
// This leverages CSS :user-invalid to instantly show feedback without interrupting typing
document.addEventListener('focusout', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        if (e.target.dataset.format === 'json') {
            try {
                // Only validate if not empty (let native 'required' handle empty state if needed)
                if (e.target.value.trim() !== '') {
                    const parsed = JSON.parse(e.target.value);
                    if (!Array.isArray(parsed)) {
                        throw new Error('Must be a JSON array');
                    }
                    // ⚡ Palette UX: Auto-format to provide positive reinforcement and prove it was parsed correctly
                    e.target.value = JSON.stringify(parsed);
                }
                e.target.setCustomValidity('');
                e.target.setAttribute('aria-invalid', 'false');
                e.target.dataset.validJson = 'true';
            } catch (err) {
                e.target.setCustomValidity('Invalid format. Please use valid JSON array format, e.g., [1, 0] or [[1,0],[0,1]]');
                e.target.setAttribute('aria-invalid', 'true');
                delete e.target.dataset.validJson;
            }
        }

        // ⚡ Palette UX: Expose validation message as a tooltip for inline feedback
        if (!e.target.validity.valid) {
            e.target.title = e.target.validationMessage;
            e.target.setAttribute('aria-invalid', 'true');
            // Proactively announce the error to screen readers
            if (typeof announceA11y === 'function') {
                const label = e.target.labels && e.target.labels.length > 0 ? e.target.labels[0].textContent.replace(/\*$/, '').trim() : 'Input';
                announceA11y(`Error in ${label}: ${e.target.validationMessage}`);
            }
        } else {
            e.target.removeAttribute('title');
            e.target.setAttribute('aria-invalid', 'false');
        }
    }
});

// Capture native 'invalid' events (e.g., on form submit) to ensure tooltips are set
document.addEventListener('invalid', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        e.target.title = e.target.validationMessage;
        e.target.setAttribute('aria-invalid', 'true');
    }
}, true);

// Clear validation errors when user types
document.addEventListener('input', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        if ('validJson' in e.target.dataset) {
            delete e.target.dataset.validJson;
        }
        // ⚡ Bolt Optimization: Wrap DOM attribute writes inside high-frequency listeners
        // with a conditional check to prevent redundant JS-to-C++ boundary crossings
        // and avoid triggering synchronous layout thrashing.
        if (e.target.validationMessage !== '') {
            e.target.setCustomValidity('');
        }
        if (e.target.getAttribute('aria-invalid') !== 'false') {
            e.target.setAttribute('aria-invalid', 'false');
        }
        if (e.target.hasAttribute('title')) {
            e.target.removeAttribute('title'); // Clear tooltip when fixing
        }

        // Clear form submit button validity on input change to allow retry
        const form = e.target.form;
        if (form) {
            const btn = form.querySelector('button[type="submit"]');
            // ⚡ Bolt Optimization: Only update DOM if validation message needs clearing to prevent layout thrashing
            if (btn && btn.validationMessage !== '') btn.setCustomValidity('');
        }

        // ⚡ UX Improvement: Mark existing output as stale to prevent confusion
        // ⚡ Bolt Optimization: Use the native O(1) form reference to find the parent section
        // instead of executing an expensive e.target.closest('section') DOM traversal on every input event.
        const section = form ? form.closest('section') : e.target.closest('section');

        // ⚡ Bolt Optimization: Early return to prevent redundant DOM queries and style recalculations
        // on every single keystroke once the section is already marked as stale.
        if (section && section.dataset.stale !== 'true') {
            section.dataset.stale = 'true';
            let didHideOutput = false;

            const chartContainer = section.querySelector('.chart-container');
            if (chartContainer && !chartContainer.querySelector('.empty-state') && !chartContainer.hasAttribute('data-empty')) {
                chartContainer.style.opacity = '0.5';
                chartContainer.style.pointerEvents = 'none';
                chartContainer.setAttribute('aria-hidden', 'true');
                didHideOutput = true;
            }
            const outputBlock = section.querySelector('.output-block[style*="display: block"]');
            if (outputBlock && outputBlock.id !== 'lqr-empty' && !outputBlock.querySelector('.empty-state') && !outputBlock.hasAttribute('data-empty')) {
                outputBlock.style.opacity = '0.5';
                outputBlock.style.pointerEvents = 'none';
                outputBlock.setAttribute('aria-hidden', 'true');
                outputBlock.querySelectorAll('.copy-btn').forEach(btn => btn.disabled = true);
                didHideOutput = true;
            }

            if (didHideOutput && typeof announceA11y === 'function') {
                announceA11y('Input changed. Previous output is now stale. Resubmit to update.');
            }
        }
    }
});

// Clear submit button validity on click to allow immediate retry
document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[type="submit"]');
    if (btn && btn.validationMessage !== '') btn.setCustomValidity('');
});

// ⚡ Bolt Optimization: Cache the Chart.js instance to prevent memory leaks and DOM thrashing
let pmpChartInstance = null;

// 1. Solve PMP
async function solvePMP() {
    const btn = document.getElementById('btn-pmp');
    const form = btn.form;
    let enabledInputs = [];
    let wasFocused = document.activeElement;
    btn.setCustomValidity('');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Solving...';
    const originalTitle = btn.getAttribute('title');
    btn.title = 'Computation in progress...';
    if (form) {
        enabledInputs = Array.from(form.elements).filter(el => !el.disabled && el !== btn);
        enabledInputs.forEach(el => el.disabled = true);
    }

    const chartContainer = document.getElementById('pmp-chart');
    if (chartContainer) {
        chartContainer.style.opacity = '0.5';
        chartContainer.style.pointerEvents = 'none';
        chartContainer.setAttribute('aria-hidden', 'true');
    }

    try {
        const payload = {
            A: [[0, 1], [-1, -1]], // Hardcoded linear system for now
            B: [[0], [1]],
            Q: [[1, 0], [0, 1]],
            R: [[1]],
            x0: parseInput('pmp-x0'),
            xf: parseInput('pmp-xf'),
            tf: parseFloatInput('pmp-tf'),
            num_points: 100
        };

        const data = await fetchWithCache('/pmp', payload);

        // Chart.js for PMP
        // ⚡ Bolt Optimization: Reuse the Chart instance and Canvas instead of destroying the DOM.
        // Updating data in-place prevents memory leaks and is much faster than destroying and recreating.
        if (pmpChartInstance) {
            pmpChartInstance.data.labels = data.t.map(t => t.toFixed(2));
            pmpChartInstance.data.datasets[0].data = data.x[0];
            pmpChartInstance.data.datasets[1].data = data.x[1];
            pmpChartInstance.data.datasets[2].data = data.u[0];
            pmpChartInstance.update();
        } else {
            let canvas = document.getElementById('pmp-canvas-inner');
            if (!canvas) {
                canvas = document.createElement('canvas');
                canvas.id = 'pmp-canvas-inner';
                canvas.setAttribute('role', 'img');
                canvas.setAttribute('aria-label', 'Optimal Trajectory Chart showing x1, x2, and u over time');
                document.getElementById('pmp-chart').replaceChildren(canvas);
            }

            pmpChartInstance = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: data.t.map(t => t.toFixed(2)),
                    datasets: [
                        { label: 'x_1(t)', data: data.x[0], borderColor: '#4a90e2', tension: 0.1, pointRadius: 0 },
                        { label: 'x_2(t)', data: data.x[1], borderColor: '#50e3c2', tension: 0.1, pointRadius: 0 },
                        { label: 'u(t)', data: data.u[0], borderColor: '#ff6b6b', tension: 0.1, pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    color: '#e0e0e0',
                    animation: false,
                    scales: {
                        x: { grid: { color: '#333' } },
                        y: { grid: { color: '#333' } }
                    }
                }
            });
        }

        if (chartContainer) {
            chartContainer.style.opacity = '';
            chartContainer.style.pointerEvents = '';
            chartContainer.removeAttribute('aria-hidden');
            chartContainer.querySelectorAll('button, input').forEach(el => el.disabled = false);
            const section = chartContainer.closest('section');
            if (section) delete section.dataset.stale;
        }

        announceA11y('PMP trajectory calculated successfully. Chart updated.');
        scrollToOutput(chartContainer);

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (err.name === 'InputValidationError') {
            wasFocused = null;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.disabled = false;
            enabledInputs.forEach(el => el.disabled = false);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to solve PMP: ' + err.message);
        btn.disabled = false;
        enabledInputs.forEach(el => el.disabled = false);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (originalTitle !== null) {
            btn.setAttribute('title', originalTitle);
        } else {
            btn.removeAttribute('title');
        }
        enabledInputs.forEach(el => el.disabled = false);
        // ⚡ Palette UX: Only restore focus if the user hasn't proactively navigated elsewhere
        if (wasFocused && typeof wasFocused.focus === 'function' && document.activeElement === document.body) {
            wasFocused.focus();
        }
    }
}

// 2. Solve LQR
async function solveLQR() {
    const btn = document.getElementById('btn-lqr');
    const form = btn.form;
    let enabledInputs = [];
    let wasFocused = document.activeElement;
    btn.setCustomValidity('');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Synthesizing...';
    const originalTitle = btn.getAttribute('title');
    btn.title = 'Computation in progress...';
    if (form) {
        enabledInputs = Array.from(form.elements).filter(el => !el.disabled && el !== btn);
        enabledInputs.forEach(el => el.disabled = true);
    }

    const outputContainer = document.getElementById('lqr-output');
    if (outputContainer) {
        outputContainer.style.opacity = '0.5';
        outputContainer.style.pointerEvents = 'none';
        outputContainer.setAttribute('aria-hidden', 'true');
        outputContainer.querySelectorAll('.copy-btn').forEach(btn => btn.disabled = true);
    }

    try {
        const payload = {
            A: parseInput('lqr-A'),
            B: parseInput('lqr-B'),
            Q: parseInput('lqr-Q'),
            R: parseInput('lqr-R')
        };

        const data = await fetchWithCache('/lqr', payload);

        // Hide empty state and show output block
        document.getElementById('lqr-empty').style.display = 'none';
        document.getElementById('lqr-output').style.display = 'block';

        document.getElementById('lqr-k-val').textContent = JSON.stringify(data.K.map(row => row.map(val => val.toFixed(4))));
        document.getElementById('lqr-poles-val').textContent = JSON.stringify(data.eigvals.map(val => val.toFixed(4)));

        if (outputContainer) {
            outputContainer.style.opacity = '';
            outputContainer.style.pointerEvents = '';
            outputContainer.removeAttribute('aria-hidden');
            outputContainer.querySelectorAll('button, input, .copy-btn').forEach(btn => btn.disabled = false);
            const section = outputContainer.closest('section');
            if (section) delete section.dataset.stale;
        }

        announceA11y('LQR synthesis complete. Gain and poles available.');
        scrollToOutput(document.getElementById('lqr-output'));

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (err.name === 'InputValidationError') {
            wasFocused = null;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.disabled = false;
            enabledInputs.forEach(el => el.disabled = false);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to synthesize LQR: ' + err.message);
        btn.disabled = false;
        enabledInputs.forEach(el => el.disabled = false);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (originalTitle !== null) {
            btn.setAttribute('title', originalTitle);
        } else {
            btn.removeAttribute('title');
        }
        enabledInputs.forEach(el => el.disabled = false);
        // ⚡ Palette UX: Only restore focus if the user hasn't proactively navigated elsewhere
        if (wasFocused && typeof wasFocused.focus === 'function' && document.activeElement === document.body) {
            wasFocused.focus();
        }
    }
}

// ⚡ Bolt Optimization: Cache the Chart.js instance to prevent memory leaks and DOM thrashing
let mpcChartInstance = null;

// 3. Solve MPC
async function solveMPC() {
    const btn = document.getElementById('btn-mpc');
    const form = btn.form;
    let enabledInputs = [];
    let wasFocused = document.activeElement;
    btn.setCustomValidity('');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Simulating...';
    const originalTitle = btn.getAttribute('title');
    btn.title = 'Computation in progress...';
    if (form) {
        enabledInputs = Array.from(form.elements).filter(el => !el.disabled && el !== btn);
        enabledInputs.forEach(el => el.disabled = true);
    }

    const chartContainer = document.getElementById('mpc-chart');
    if (chartContainer) {
        chartContainer.style.opacity = '0.5';
        chartContainer.style.pointerEvents = 'none';
        chartContainer.setAttribute('aria-hidden', 'true');
    }

    try {
        const payload = {
            A: [[0, 1], [-1, -1]], // Continuous time system matching the backend
            B: [[0], [1]],
            Q: [[1, 0], [0, 1]],
            R: [[1]],
            x0: [5.0, 0.0],
            N_horizon: parseInt(document.getElementById('mpc-N').value),
            dt: parseFloatInput('mpc-dt'),
            u_min: parseInput('mpc-umin'),
            u_max: parseInput('mpc-umax')
        };

        const data = await fetchWithCache('/mpc', payload);

        // Chart.js for MPC
        // ⚡ Bolt Optimization: Reuse the Chart instance and Canvas instead of destroying the DOM.
        // Tearing down the canvas without calling chart.destroy() causes severe memory leaks
        // as Chart.js retains event listeners. Updating data in-place is also much faster.
        if (mpcChartInstance) {
            mpcChartInstance.data.labels = data.t.map(t => t.toFixed(1));
            mpcChartInstance.data.datasets[0].data = data.x[0];
            mpcChartInstance.data.datasets[1].data = data.x[1];
            mpcChartInstance.data.datasets[2].data = data.u[0];
            mpcChartInstance.update();
        } else {
            let canvas = document.getElementById('mpc-canvas-inner');
            if (!canvas) {
                canvas = document.createElement('canvas');
                canvas.id = 'mpc-canvas-inner';
                canvas.setAttribute('role', 'img');
                canvas.setAttribute('aria-label', 'Model Predictive Control Simulation Chart showing predicted states and inputs');
                document.getElementById('mpc-chart').replaceChildren(canvas);
            }

            mpcChartInstance = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: data.t.map(t => t.toFixed(1)),
                    datasets: [
                        { label: 'x_1', data: data.x[0], borderColor: '#4a90e2', tension: 0.1 },
                        { label: 'x_2', data: data.x[1], borderColor: '#50e3c2', tension: 0.1 },
                        { label: 'u', data: data.u[0], borderColor: '#ff6b6b', tension: 0.1, stepped: true }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    color: '#e0e0e0',
                    animation: false,
                    scales: {
                        x: { grid: { color: '#333' } },
                        y: { grid: { color: '#333' } }
                    }
                }
            });
        }

        if (chartContainer) {
            chartContainer.style.opacity = '';
            chartContainer.style.pointerEvents = '';
            chartContainer.removeAttribute('aria-hidden');
            chartContainer.querySelectorAll('button, input').forEach(el => el.disabled = false);
            const section = chartContainer.closest('section');
            if (section) delete section.dataset.stale;
        }

        announceA11y('MPC simulation complete. Chart updated.');
        scrollToOutput(chartContainer);

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (err.name === 'InputValidationError') {
            wasFocused = null;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.disabled = false;
            enabledInputs.forEach(el => el.disabled = false);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to simulate MPC: ' + err.message);
        btn.disabled = false;
        enabledInputs.forEach(el => el.disabled = false);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
        if (originalTitle !== null) {
            btn.setAttribute('title', originalTitle);
        } else {
            btn.removeAttribute('title');
        }
        enabledInputs.forEach(el => el.disabled = false);
        // ⚡ Palette UX: Only restore focus if the user hasn't proactively navigated elsewhere
        if (wasFocused && typeof wasFocused.focus === 'function' && document.activeElement === document.body) {
            wasFocused.focus();
        }
    }
}

// ⚡ Palette UX: Auto-scroll Helper
// Smoothly scrolls to the generated output so users on mobile/small screens
// don't miss the result. Respects the user's reduced motion preference.
function scrollToOutput(element) {
    if (element) {
        const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        element.scrollIntoView({ behavior: behavior, block: 'nearest' });
    }
}

// ⚡ Palette UX: Accessibility Announcer Helper
// Handles dynamic screen reader announcements and prevents identical consecutive
// messages from being ignored by mutating the text with a zero-width space.
let a11yTimeoutId = null;
function announceA11y(message) {
    const announcer = document.getElementById('a11y-announcer');
    if (!announcer) return;

    // Clear previous timeout to prevent premature erasure of rapid messages
    if (a11yTimeoutId) {
        clearTimeout(a11yTimeoutId);
    }

    // If exact same message, append zero-width space to force DOM mutation
    if (announcer.textContent === message) {
        announcer.textContent = message + '\u200B';
    } else {
        announcer.textContent = message;
    }

    a11yTimeoutId = setTimeout(() => {
        announcer.textContent = '';
    }, 3000);
}

// Initialize events and rendering once DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
    // Setup copy buttons
    document.querySelectorAll('.copy-btn').forEach(copyBtn => {
        copyBtn.addEventListener('click', async function() {
            if (this.disabled || this.dataset.copying === 'true') return;
            const targetId = this.dataset.target;
            const valElement = document.getElementById(targetId);
            const val = valElement ? valElement.textContent : null;

            if (val && val !== '...') {
                try {
                    this.dataset.copying = 'true'; // Prevent overlapping rapid clicks without losing focus
                    await navigator.clipboard.writeText(val);
                    const span = this.querySelector('span');
                    const originalLabel = this.getAttribute('aria-label');
                    const originalTitle = this.getAttribute('title');

                    span.textContent = '✅';
                    this.setAttribute('aria-label', 'Copied successfully');
                    this.setAttribute('title', 'Copied successfully!');

                    // Use the original label (e.g. "Copy Gain K matrix to clipboard") to create a contextual message.
                    // If the label is like "Copy Gain K matrix to clipboard", we can strip " to clipboard" or "Copy "
                    // Or just use `originalLabel + ' successfully'` which is safe.
                    let announceMsg = 'Copied successfully!';
                    if (originalLabel) {
                        // Extract what is being copied. Example: "Copy Gain K matrix to clipboard" -> "Gain K matrix"
                        const match = originalLabel.match(/Copy (.*?) to clipboard/i) || originalLabel.match(/Copy (.*)/i);
                        if (match && match[1]) {
                            announceMsg = match[1] + ' copied successfully!';
                        } else {
                            announceMsg = originalLabel + ' successfully!';
                        }
                    }
                    announceA11y(announceMsg);

                    setTimeout(() => {
                        span.textContent = '📋';
                        this.setAttribute('aria-label', originalLabel);
                        if (originalTitle !== null) {
                            this.setAttribute('title', originalTitle);
                        } else {
                            this.removeAttribute('title');
                        }
                        delete this.dataset.copying;
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy!', err);
                    delete this.dataset.copying;
                }
            }
        });
    });

    // ⚡ Bolt Optimization: Use ignoredTags and ignoredClasses for KaTeX initialization.
    // This prevents KaTeX from scanning heavy, unrelated DOM sub-trees (like Three.js canvases and Chart.js containers),
    // which causes severe initialization overhead and main thread blocking, while safely keeping the fallback on document.body.
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(document.body, {
            ignoredClasses: ["chart-container"],
            ignoredTags: ["canvas", "script", "noscript", "style", "textarea", "pre", "code", "option"]
        });
    }

    // Attach form submit listeners
    const pmpForm = document.getElementById('pmp-form');
    if (pmpForm) {
        pmpForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solvePMP();
        });
    }

    const lqrForm = document.getElementById('lqr-form');
    if (lqrForm) {
        lqrForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solveLQR();
        });
    }

    const mpcForm = document.getElementById('mpc-form');
    if (mpcForm) {
        mpcForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solveMPC();
        });
    }
});

// ⚡ Palette: Add keyboard shortcuts for power users to quickly submit forms.
// This improves the UX for users who prefer keyboard navigation.
document.addEventListener('DOMContentLoaded', () => {
    // Detect Mac for shortcut hints
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    if (isMac) {
        document.querySelectorAll('.shortcut-modifier').forEach(el => {
            el.textContent = '⌘';
        });
        document.querySelectorAll('[aria-keyshortcuts="Control+Enter"]').forEach(el => {
            el.setAttribute('aria-keyshortcuts', 'Meta+Enter');
        });
    }
});

document.addEventListener('keydown', (e) => {
    // Check if Ctrl+Enter or Cmd+Enter is pressed
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement) {
            const form = activeElement.form || activeElement.closest('form');
            if (form) {
                // Prevent default Enter behavior
                e.preventDefault();
                const submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                }
            }
        }
    }
});

// ⚡ Palette: Prevent accidental value changes on number inputs when scrolling
document.addEventListener('wheel', (e) => {
    if (document.activeElement.type === 'number' && document.activeElement.classList.contains('ui-input')) {
        document.activeElement.blur();
    }
}, { passive: true });

// ⚡ Palette: Auto-select input text on focus to make overwriting complex pre-filled values faster
document.addEventListener('focusin', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        e.target.select();
    }
});
