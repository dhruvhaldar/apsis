// --- Three.js Background Setup ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

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
const material = new THREE.PointsMaterial({ color: 0x4a90e2, size: 2, transparent: true, opacity: 0.5 });
const particles = new THREE.Points(geometry, material);
scene.add(particles);

camera.position.z = 1000;

function animate() {
    requestAnimationFrame(animate);
    particles.rotation.x += 0.0001;
    particles.rotation.y += 0.0002;
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
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

    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) await handleApiError(response);
    const data = await response.json();
    apiCache.set(cacheKey, data);
    return data;
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
        return JSON.parse(el.value);
    } catch (e) {
        el.setCustomValidity('Invalid format. Please use valid JSON array format, e.g., [1, 0] or [[1,0],[0,1]]');
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
        el.reportValidity();
        el.focus();
        const err = new Error(`Invalid number in ${id}`);
        err.name = 'InputValidationError';
        throw err;
    }
    return val;
}

// Clear validation errors when user types
document.addEventListener('input', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        e.target.setCustomValidity('');

        // ⚡ UX Improvement: Mark existing output as stale to prevent confusion
        const section = e.target.closest('section');
        if (section) {
            const chartContainer = section.querySelector('.chart-container');
            if (chartContainer && !chartContainer.querySelector('.empty-state')) {
                chartContainer.style.opacity = '0.5';
                chartContainer.style.pointerEvents = 'none';
                chartContainer.setAttribute('aria-hidden', 'true');
            }
            const outputBlock = section.querySelector('.output-block[style*="display: block"]');
            if (outputBlock && outputBlock.id !== 'lqr-empty') {
                outputBlock.style.opacity = '0.5';
                outputBlock.style.pointerEvents = 'none';
                outputBlock.setAttribute('aria-hidden', 'true');
                outputBlock.querySelectorAll('.copy-btn').forEach(btn => btn.disabled = true);
            }
        }
    }
    // Clear form submit button validity on input change to allow retry
    const form = e.target.closest('form');
    if (form) {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) btn.setCustomValidity('');
    }
});

// Clear submit button validity on click to allow immediate retry
document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[type="submit"]');
    if (btn) btn.setCustomValidity('');
});

// 1. Solve PMP
async function solvePMP() {
    const btn = document.getElementById('btn-pmp');
    let wasFocused = document.activeElement === btn;
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span aria-hidden="true">⏳</span> Solving...';

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

        // Plotly Chart for PMP
        const traceX1 = { x: data.t, y: data.x[0], mode: 'lines', name: 'x_1(t)', line: {color: '#4a90e2'} };
        const traceX2 = { x: data.t, y: data.x[1], mode: 'lines', name: 'x_2(t)', line: {color: '#50e3c2'} };
        const traceU = { x: data.t, y: data.u[0], mode: 'lines', name: 'u(t)', line: {color: '#e24a4a'} };

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#e0e0e0' },
            margin: { l: 40, r: 20, b: 40, t: 20 },
            xaxis: { gridcolor: '#333' },
            yaxis: { gridcolor: '#333' }
        };

        // ⚡ Bolt Optimization: Use Plotly.react instead of Plotly.newPlot for subsequent updates.
        // newPlot destroys the DOM element and recreates it. react updates the data/layout in-place
        // via diffing, saving significant main-thread time and preventing visual flickering on re-solves.
        Plotly.react('pmp-chart', [traceX1, traceX2, traceU], layout, {responsive: true});

        if (chartContainer) {
            chartContainer.style.opacity = '';
            chartContainer.style.pointerEvents = '';
            chartContainer.removeAttribute('aria-hidden');
            chartContainer.querySelectorAll('button, input').forEach(el => el.disabled = false);
        }

        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            announcer.innerText = 'PMP trajectory calculated successfully. Chart updated.';
            setTimeout(() => { announcer.innerText = ''; }, 3000);
        }

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (err.name === 'InputValidationError') {
            wasFocused = false;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to solve PMP: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (wasFocused) btn.focus();
    }
}

// 2. Solve LQR
async function solveLQR() {
    const btn = document.getElementById('btn-lqr');
    let wasFocused = document.activeElement === btn;
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span aria-hidden="true">⏳</span> Synthesizing...';

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

        document.getElementById('lqr-k-val').innerText = JSON.stringify(data.K.map(row => row.map(val => val.toFixed(4))));
        document.getElementById('lqr-poles-val').innerText = JSON.stringify(data.eigvals.map(val => val.toFixed(4)));

        if (outputContainer) {
            outputContainer.style.opacity = '';
            outputContainer.style.pointerEvents = '';
            outputContainer.removeAttribute('aria-hidden');
            outputContainer.querySelectorAll('button, input, .copy-btn').forEach(btn => btn.disabled = false);
        }

        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            announcer.innerText = 'LQR synthesis complete. Gain and poles available.';
            setTimeout(() => { announcer.innerText = ''; }, 3000);
        }

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (err.name === 'InputValidationError') {
            wasFocused = false;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to synthesize LQR: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (wasFocused) btn.focus();
    }
}

// ⚡ Bolt Optimization: Cache the Chart.js instance to prevent memory leaks and DOM thrashing
let mpcChartInstance = null;

// 3. Solve MPC
async function solveMPC() {
    const btn = document.getElementById('btn-mpc');
    let wasFocused = document.activeElement === btn;
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<span aria-hidden="true">⏳</span> Simulating...';

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
                document.getElementById('mpc-chart').innerHTML = '';
                document.getElementById('mpc-chart').appendChild(canvas);
            }

            mpcChartInstance = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: data.t.map(t => t.toFixed(1)),
                    datasets: [
                        { label: 'x_1', data: data.x[0], borderColor: '#4a90e2', tension: 0.1 },
                        { label: 'x_2', data: data.x[1], borderColor: '#50e3c2', tension: 0.1 },
                        { label: 'u', data: data.u[0], borderColor: '#e24a4a', tension: 0.1, stepped: true }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    color: '#e0e0e0',
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
        }

        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            announcer.innerText = 'MPC simulation complete. Chart updated.';
            setTimeout(() => { announcer.innerText = ''; }, 3000);
        }

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (err.name === 'InputValidationError') {
            wasFocused = false;
            return;
        }
        if (err.name === 'ValidationError') {
            btn.setCustomValidity(err.message);
            btn.reportValidity();
            return;
        }
        btn.setCustomValidity('Failed to simulate MPC: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        if (wasFocused) btn.focus();
    }
}

// Initialize events and rendering once DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
    // Setup copy buttons
    document.querySelectorAll('.copy-btn').forEach(copyBtn => {
        copyBtn.addEventListener('click', async function() {
            if (this.disabled) return;
            const targetId = this.dataset.target;
            const valElement = document.getElementById(targetId);
            const val = valElement ? valElement.innerText : null;

            if (val && val !== '...') {
                try {
                    const wasFocused = document.activeElement === this;
                    this.disabled = true; // Prevent overlapping rapid clicks
                    await navigator.clipboard.writeText(val);
                    const span = this.querySelector('span');
                    const originalLabel = this.getAttribute('aria-label');
                    const originalTitle = this.getAttribute('title');

                    span.innerText = '✅';
                    this.setAttribute('aria-label', 'Copied successfully');
                    this.setAttribute('title', 'Copied successfully!');

                    const announcer = document.getElementById('a11y-announcer');
                    if (announcer) {
                        announcer.innerText = 'Copied successfully!';
                        setTimeout(() => { announcer.innerText = ''; }, 3000);
                    }

                    setTimeout(() => {
                        span.innerText = '📋';
                        this.setAttribute('aria-label', originalLabel);
                        if (originalTitle !== null) {
                            this.setAttribute('title', originalTitle);
                        } else {
                            this.removeAttribute('title');
                        }
                        this.disabled = false;
                        if (wasFocused) this.focus();
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy!', err);
                    this.disabled = false;
                    if (wasFocused) this.focus();
                }
            }
        });
    });

    // Initialize KaTeX
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(document.body);
    }

    // Helper to dim output containers when input changes
    function setOutputStale(containerId) {
        const container = document.getElementById(containerId);
        if (container && !container.hasAttribute('data-empty')) {
            container.style.opacity = '0.5';
            container.style.pointerEvents = 'none';
            container.setAttribute('aria-hidden', 'true');
            container.querySelectorAll('button, input').forEach(el => el.disabled = true);
        }
    }

    // Helper to restore output containers after successful calculation
    window.clearOutputStale = function(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.opacity = '';
            container.style.pointerEvents = '';
            container.removeAttribute('aria-hidden');
            container.querySelectorAll('button, input, .copy-btn').forEach(el => el.disabled = false);
        }
    };

    // Attach form submit listeners
    const pmpForm = document.getElementById('pmp-form');
    if (pmpForm) {
        pmpForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solvePMP();
        });
        pmpForm.addEventListener('input', () => setOutputStale('pmp-chart'));
    }

    const lqrForm = document.getElementById('lqr-form');
    if (lqrForm) {
        lqrForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solveLQR();
        });
        lqrForm.addEventListener('input', () => setOutputStale('lqr-output'));
    }

    const mpcForm = document.getElementById('mpc-form');
    if (mpcForm) {
        mpcForm.addEventListener('submit', (e) => {
            e.preventDefault();
            solveMPC();
        });
        mpcForm.addEventListener('input', () => setOutputStale('mpc-chart'));
    }
});
