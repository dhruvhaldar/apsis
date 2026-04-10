// --- Three.js Background Setup ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('three-canvas').appendChild(renderer.domElement);

const geometry = new THREE.BufferGeometry();
const vertices = [];
for (let i = 0; i < 5000; i++) {
    vertices.push(
        THREE.MathUtils.randFloatSpread(2000),
        THREE.MathUtils.randFloatSpread(2000),
        THREE.MathUtils.randFloatSpread(2000)
    );
}
geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
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

// Utility to parse JSON array strings safely
function parseInput(id) {
    const el = document.getElementById(id);
    try {
        return JSON.parse(el.value);
    } catch (e) {
        el.setCustomValidity('Invalid format. Please use valid JSON array format, e.g., [1, 0] or [[1,0],[0,1]]');
        el.reportValidity();
        el.focus();
        throw e;
    }
}

function parseFloatInput(id) {
    const el = document.getElementById(id);
    const val = parseFloat(el.value);
    if (isNaN(val)) {
        el.setCustomValidity('Please enter a valid number.');
        el.reportValidity();
        el.focus();
        throw new Error(`Invalid number in ${id}`);
    }
    return val;
}

// Clear validation errors when user types
document.addEventListener('input', (e) => {
    if (e.target && e.target.classList.contains('ui-input')) {
        e.target.setCustomValidity('');
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
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerText = '⏳ Solving...';

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

        const response = await fetch(`${API_BASE}/pmp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();

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

        Plotly.newPlot('pmp-chart', [traceX1, traceX2, traceU], layout, {responsive: true});

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        btn.setCustomValidity('Failed to solve PMP: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
    }
}

// 2. Solve LQR
async function solveLQR() {
    const btn = document.getElementById('btn-lqr');
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerText = '⏳ Synthesizing...';

    try {
        const payload = {
            A: parseInput('lqr-A'),
            B: parseInput('lqr-B'),
            Q: parseInput('lqr-Q'),
            R: parseInput('lqr-R')
        };

        const response = await fetch(`${API_BASE}/lqr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();

        // Hide empty state and show output block
        document.getElementById('lqr-empty').style.display = 'none';
        document.getElementById('lqr-output').style.display = 'block';

        document.getElementById('lqr-k-val').innerText = JSON.stringify(data.K.map(row => row.map(val => val.toFixed(4))));
        document.getElementById('lqr-poles-val').innerText = JSON.stringify(data.eigvals.map(val => val.toFixed(4)));

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        btn.setCustomValidity('Failed to synthesize LQR: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
    }
}

// 3. Solve MPC
async function solveMPC() {
    const btn = document.getElementById('btn-mpc');
    btn.setCustomValidity('');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.setAttribute('aria-busy', 'true');
    btn.innerText = '⏳ Simulating...';

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

        const response = await fetch(`${API_BASE}/mpc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();

        // Chart.js for MPC
        const ctx = document.getElementById('mpc-canvas-inner');
        if (ctx) ctx.remove(); // Clear previous

        const canvas = document.createElement('canvas');
        canvas.id = 'mpc-canvas-inner';
        document.getElementById('mpc-chart').innerHTML = '';
        document.getElementById('mpc-chart').appendChild(canvas);

        new Chart(canvas, {
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

    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
        btn.setCustomValidity('Failed to simulate MPC: ' + err.message);
        btn.reportValidity();
    } finally {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
        btn.innerText = originalText;
    }
}

// Initialize events and rendering once DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
    // Setup copy button
    const copyBtn = document.getElementById('lqr-copy-k');
    let isCopying = false;
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            if (isCopying) return;
            const kVal = document.getElementById('lqr-k-val').innerText;
            if (kVal && kVal !== '...') {
                try {
                    isCopying = true;
                    await navigator.clipboard.writeText(kVal);
                    const span = copyBtn.querySelector('span');
                    const originalLabel = copyBtn.getAttribute('aria-label');

                    span.innerText = '✅';
                    copyBtn.setAttribute('aria-label', 'Copied successfully');

                    setTimeout(() => {
                        span.innerText = '📋';
                        copyBtn.setAttribute('aria-label', originalLabel);
                        isCopying = false;
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy!', err);
                    isCopying = false;
                }
            }
        });
    }

    // Initialize KaTeX
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(document.body);
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
