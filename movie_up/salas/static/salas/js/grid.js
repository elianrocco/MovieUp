const CELL_CLASS_MAP = Object.freeze({
    P: "celda--pasillo",
    A: "celda--asiento",
    R: "celda--reservado",
});

const CELL_LABEL_MAP = Object.freeze({
    P: "Pasillo",
    A: "Asiento",
    R: "Reservado",
});

const CELL_CYCLE = ["P", "A", "R"];
const DEFAULT_SIZE = 10;
const MAX_SIZE = 100;

function readInitialDistribution() {
    const stateElement = document.getElementById("initial-distribution");
    if (!stateElement) {
        return null;
    }

    try {
        const value = JSON.parse(stateElement.textContent);
        if (!value || !Array.isArray(value.filas) || value.filas.length === 0) {
            return null;
        }

        const rows = value.filas.map((row) => {
            if (typeof row !== "string") {
                return null;
            }
            return [...row.replace(/\s/g, "").toUpperCase()];
        });

        if (
            rows.some((row) => row === null || row.length === 0 || row.some((cell) => !CELL_CYCLE.includes(cell)))
        ) {
            return null;
        }

        const width = rows[0].length;
        if (
            rows.length > MAX_SIZE ||
            width > MAX_SIZE ||
            rows.some((row) => row.length !== width)
        ) {
            return null;
        }

        return { rows, version: Number.isInteger(value.version) ? value.version : 1 };
    } catch (_error) {
        return null;
    }
}

function initializeDistributionEditor() {
    const grid = document.querySelector("[data-seat-grid]");
    if (!grid) {
        return;
    }

    const form = grid.closest("form");
    const widthInput = document.querySelector("[data-grid-width]");
    const heightInput = document.querySelector("[data-grid-height]");
    const resizeButton = document.querySelector("[data-grid-resize]");
    const distributionInput = document.querySelector("[data-distribution-input]");
    const initial = readInitialDistribution();

    let matrix = initial
        ? initial.rows
        : Array.from({ length: DEFAULT_SIZE }, () => Array(DEFAULT_SIZE).fill("P"));
    let version = initial ? initial.version : 1;

    const serialize = () => {
        distributionInput.value = JSON.stringify({
            version,
            filas: matrix.map((row) => row.join("")),
        });
    };

    const render = () => {
        const width = matrix[0].length;
        grid.style.setProperty("--grid-columns", width);
        grid.replaceChildren();

        matrix.forEach((row, rowIndex) => {
            row.forEach((cell, columnIndex) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = `seat-grid__cell ${CELL_CLASS_MAP[cell]}`;
                button.dataset.row = rowIndex;
                button.dataset.column = columnIndex;
                button.dataset.type = cell;
                button.setAttribute("aria-label", CELL_LABEL_MAP[cell]);
                button.title = CELL_LABEL_MAP[cell];
                grid.append(button);
            });
        });

        widthInput.value = width;
        heightInput.value = matrix.length;
        serialize();
    };

    grid.addEventListener("click", (event) => {
        const cell = event.target.closest("button[data-row][data-column]");
        if (!cell || !grid.contains(cell)) {
            return;
        }

        const rowIndex = Number(cell.dataset.row);
        const columnIndex = Number(cell.dataset.column);
        const currentIndex = CELL_CYCLE.indexOf(matrix[rowIndex][columnIndex]);
        matrix[rowIndex][columnIndex] = CELL_CYCLE[(currentIndex + 1) % CELL_CYCLE.length];
        render();
    });

    resizeButton.addEventListener("click", () => {
        if (!widthInput.reportValidity() || !heightInput.reportValidity()) {
            return;
        }

        const width = Number(widthInput.value);
        const height = Number(heightInput.value);
        if (
            !Number.isInteger(width) ||
            !Number.isInteger(height) ||
            width < 1 ||
            width > MAX_SIZE ||
            height < 1 ||
            height > MAX_SIZE
        ) {
            return;
        }

        matrix = Array.from({ length: height }, (_, rowIndex) =>
            Array.from({ length: width }, (_, columnIndex) => matrix[rowIndex]?.[columnIndex] ?? "P"),
        );
        render();
    });

    form.addEventListener("submit", serialize);
    render();
}

document.addEventListener("DOMContentLoaded", initializeDistributionEditor);
