document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("gemini-btn");
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("gemini-result");
    const emptyState = document.getElementById("empty-state");
    const customNote = document.getElementById("custom-note");
    const chips = document.querySelectorAll(".chip");
    const errorBox = document.getElementById("error-box");

    function getSelectedValues(selector) {
        return Array.from(document.querySelectorAll(selector))
            .filter((el) => el.classList.contains("active"))
            .map((el) => el.dataset.value)
            .filter(Boolean);
    }

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function renderRecommendations(recommendations) {
        if (!resultBox) return;

        if (!recommendations || recommendations.length === 0) {
            resultBox.innerHTML = `
                <div class="empty-state">
                    Aucune suggestion n’a été générée. Essaie avec d’autres filtres.
                </div>
            `;
            resultBox.classList.remove("hidden");
            if (emptyState) emptyState.classList.add("hidden");
            return;
        }

        const cards = recommendations.map((item) => {
            const title = escapeHtml(item.nom_de_serie || "Série recommandée");
            const genre = escapeHtml(item.genre || "Non précisé");
            const match = escapeHtml(String(item.niveau_match || "90"));
            const why = escapeHtml(item.pourquoi_ce_choix || "");
            const resume = escapeHtml(item.resume || "");
            const image = escapeHtml(item.image || "");

            const imageBlock = image
                ? `<img class="recommendation-image" src="${image}" alt="${title}">`
                : `<div class="recommendation-image placeholder-image">Image indisponible</div>`;

            return `
                <article class="recommendation-card">
                    <div class="recommendation-poster">
                        ${imageBlock}
                    </div>

                    <div class="recommendation-content">
                        <div class="recommendation-top">
                            <h4 class="recommendation-title">${title}</h4>
                            <span class="match-badge">${match}% match</span>
                        </div>

                        <div class="meta-row">
                            <span class="meta-pill">${genre}</span>
                        </div>

                        <div class="recommendation-section">
                            <h4>Pourquoi ce choix</h4>
                            <p>${why}</p>
                        </div>

                        <div class="recommendation-section">
                            <h4>Résumé</h4>
                            <p>${resume}</p>
                        </div>
                    </div>
                </article>
            `;
        }).join("");

        resultBox.innerHTML = cards;
        resultBox.classList.remove("hidden");
        if (emptyState) emptyState.classList.add("hidden");
    }

    function clearError() {
        if (!errorBox) return;
        errorBox.textContent = "";
        errorBox.classList.add("hidden");
    }

    function showError(message) {
        if (!errorBox) return;
        errorBox.textContent = message;
        errorBox.classList.remove("hidden");
    }

    chips.forEach((chip) => {
        chip.addEventListener("click", () => {
            chip.classList.toggle("active");
        });
    });

    if (!button) return;

    button.addEventListener("click", async () => {
        clearError();

        const genres = getSelectedValues(".genre-chip");
        const moods = getSelectedValues(".mood-chip");
        const paces = getSelectedValues(".pace-chip");
        const styles = getSelectedValues(".style-chip");
        const popularity = getSelectedValues(".popularity-chip");
        const formats = getSelectedValues(".format-chip");
        const extra = customNote ? customNote.value.trim() : "";

        const totalSelected =
            genres.length +
            moods.length +
            paces.length +
            styles.length +
            popularity.length +
            formats.length;

        if (totalSelected === 0 && !extra) {
            showError("Choisis au moins un filtre.");
            return;
        }

        loading?.classList.remove("hidden");
        resultBox?.classList.add("hidden");
        if (resultBox) resultBox.innerHTML = "";

        try {
            const response = await fetch("/api/recommendations/gemini", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    genres,
                    moods,
                    paces,
                    styles,
                    popularity,
                    formats,
                    extra
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || "Erreur lors de la génération.");
                return;
            }

            renderRecommendations(data.recommendations || []);
        } catch (error) {
            showError("Erreur de connexion au serveur.");
        } finally {
            loading?.classList.add("hidden");
        }
    });
});