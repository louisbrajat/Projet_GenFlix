document.addEventListener("DOMContentLoaded", () => {
    initFilterGeminiRecommendations();
    initRecommendationOverlays();
});

/* =========================
   TA GENERATION (FILTRES)
========================= */
function initFilterGeminiRecommendations() {
    const button = document.getElementById("gemini-btn");
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("gemini-result");
    const emptyState = document.getElementById("empty-state");
    const errorBox = document.getElementById("error-box");
    const customNote = document.getElementById("custom-note");
    const chips = document.querySelectorAll(".chip");

    if (!button) return;

    function getSelectedValues(selector) {
        return Array.from(document.querySelectorAll(selector))
            .filter(el => el.classList.contains("active"))
            .map(el => el.dataset.value)
            .filter(Boolean);
    }

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function showError(message) {
        if (!errorBox) return;
        errorBox.textContent = message;
        errorBox.classList.remove("hidden");
    }

    function clearError() {
        if (!errorBox) return;
        errorBox.textContent = "";
        errorBox.classList.add("hidden");
    }

    /* 🔥 RENDER PROPRE */
    function renderRecommendations(recommendations) {
    if (!resultBox) return;

    if (!recommendations || recommendations.length === 0) {
        resultBox.innerHTML = `<p class="empty-state">Aucune suggestion.</p>`;
        resultBox.classList.remove("hidden");
        return;
    }

    const html = `
        <div class="bodySerie">
            <div class="MesSeries" id="MesSeries">
                <div class="listeSerie">
                    ${recommendations.map(s => {
                        const genres = (s.genres || [])
                            .map(g => `<span class="badge">${g}</span>`)
                            .join("");

                        return `
                            <div class="film">
                                <div class="contenant serie-item" data-title="${s.name}">
                                    <div class="affiche">
                                        <img class="img_film" src="${s.img}" alt="${s.name}">
                                    </div>
                                    <div class="titreFilm">
                                        <p>${s.name}</p>
                                    </div>
                                    <div class="bottomFilm">
                                        <button class="butEnsavoirplus" data-id-key="${s.idserimaze}">
                                            En savoir +
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="Hoverinformation" id="info-${s.idserimaze}">
                                <div class="info-content">
                                    <div class="info-poster">
                                        <img src="${s.imgbig}" alt="${s.name}">
                                    </div>

                                    <div class="info-corp">
                                        <div class="info-header">
                                            <div class="info-title-area">
                                                <h2>${s.name}</h2>
                                                <div class="meta-data">
                                                    <span class="note-globale">★ <strong>${s.note}</strong>/10</span>
                                                    <div class="genres">
                                                        ${genres}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="info-body">
                                            <div class="section">
                                                <h4>L'avis de l'IA</h4>
                                                <p class="explication">${s.explication || ""}</p>
                                            </div>

                                            <div class="section">
                                                <h4>Pourquoi regarder ?</h4>
                                                <p class="donner-envie">${s.donnerenvi || ""}</p>
                                            </div>

                                            <div class="section OHHH">
                                                <h4>Résumé</h4>
                                                <p>${s.resume || ""}</p>
                                            </div>

                                            <div class="section">
                                                <h4>Une petite Référence</h4>
                                                <p class="ref">${s.ref || ""}</p>
                                            </div>

                                            <div class="section">
                                                <h4>Une petite Faim</h4>
                                                <p class="repas">${s.repas || ""}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join("")}
                </div>
            </div>
        </div>
    `;

    resultBox.innerHTML = html;
    resultBox.classList.remove("hidden");
    emptyState?.classList.add("hidden");
}


    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            chip.classList.toggle("active");
        });
    });

    button.addEventListener("click", async () => {
        clearError();

        const genres = getSelectedValues(".genre-chip");
        const moods = getSelectedValues(".mood-chip");
        const paces = getSelectedValues(".pace-chip");
        const styles = getSelectedValues(".style-chip");
        const popularity = getSelectedValues(".popularity-chip");
        const formats = getSelectedValues(".format-chip");
        const extra = customNote ? customNote.value.trim() : "";

        if (
            !genres.length &&
            !moods.length &&
            !paces.length &&
            !styles.length &&
            !popularity.length &&
            !formats.length &&
            !extra
        ) {
            showError("Choisis au moins un filtre.");
            return;
        }

        loading?.classList.remove("hidden");
        resultBox?.classList.add("hidden");

        try {
            const response = await fetch("/api/recommendations/gemini/filters", {
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
                showError(data.error || "Erreur serveur");
                return;
            }

            renderRecommendations(data.recommendations);
        } catch (error) {
            showError("Erreur connexion serveur");
        } finally {
            loading?.classList.add("hidden");
        }
    });
}

/* =========================
   OVERLAY (NE PAS TOUCHER)
========================= */
function initRecommendationOverlays() {
    document.addEventListener("click", (e) => {
        const button = e.target.closest(".butEnsavoirplus");

        if (button) {
            e.preventDefault();
            const serieId = button.dataset.idKey;
            const targetInfo = document.getElementById(`info-${serieId}`);

            if (targetInfo) {
                targetInfo.style.display = "flex";
                document.body.style.overflow = "hidden";
            }
            return;
        }

        const overlay = e.target.closest(".Hoverinformation");

        if (overlay && e.target === overlay) {
            overlay.style.display = "none";
            document.body.style.overflow = "auto";
        }
    });
}