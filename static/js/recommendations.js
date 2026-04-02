document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("gemini-btn");
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("gemini-result");
    const resultText = document.getElementById("gemini-text");
    const promptInput = document.getElementById("prompt-input");
    const customNote = document.getElementById("custom-note");
    const refreshPromptBtn = document.getElementById("refresh-prompt-btn");
    const seriesCards = document.querySelectorAll(".serie-item");
    const chips = document.querySelectorAll(".chip");

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

            return `
                <article class="recommendation-card">
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

    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            chip.classList.toggle("active");
            buildPrompt();
        });
    });

    if (customNote) {
        customNote.addEventListener("input", buildPrompt);
    }

    if (refreshPromptBtn) {
        refreshPromptBtn.addEventListener("click", buildPrompt);
    }

    buildPrompt();

    if (!button) return;

    button.addEventListener("click", async () => {
        const prompt = promptInput ? promptInput.value.trim() : "";

        const lastSeries = Array.from(seriesCards)
            .map(card => card.dataset.title)
            .filter(Boolean);

        if (!prompt) {
            alert("Veuillez écrire un prompt.");
            return;
        }

        if (lastSeries.length === 0) {
            alert("Aucune série disponible pour générer des recommandations.");
            return;
        }

        loading?.classList.remove("hidden");
        resultBox?.classList.add("hidden");
        if (resultText) resultText.textContent = "";

        try {
            const response = await fetch("/api/recommendations/gemini", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    prompt: prompt,
                    last_series: lastSeries
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (resultText) {
                    resultText.textContent = data.error || "Erreur lors de la génération.";
                }
            } else {
                if (resultText) {
                    resultText.textContent = data.result;
                }
            }

            resultBox?.classList.remove("hidden");
        } catch (error) {
            if (resultText) {
                resultText.textContent = "Erreur de connexion au serveur.";
            }
            resultBox?.classList.remove("hidden");
        } finally {
            loading?.classList.add("hidden");
        }
    });
});






const buttons = document.querySelectorAll('.butEnsavoirplus');

const overlays = document.querySelectorAll('.Hoverinformation');

buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const serieId = btn.dataset.idKey;
            const targetInfo = document.getElementById(`info-${serieId}`);

            if (targetInfo) {
                targetInfo.style.display = 'flex'; // 'flex' pour centrer le contenu
                document.body.style.overflow = 'hidden'; // Bloque le scroll
            }
        });
    });

  overlays.forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            // Ferme uniquement si on clique sur le fond noir (l'overlay)
            // et non sur la boîte blanche (le contenu)
            if (e.target === this) {
                this.style.display = 'none';
                document.body.style.overflow = 'auto'; // Réactive le scroll
            }
        });
    });

    // Optionnel : Fermer avec la touche Échap
    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape") {
            overlays.forEach(ov => {
                if (ov.style.display === 'flex') {
                    ov.style.display = 'none';
                    document.body.style.overflow = 'auto';
                }
            });
        }
    });