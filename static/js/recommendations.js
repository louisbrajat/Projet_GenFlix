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

    function buildPrompt() {
        const genres = getSelectedValues(".genre-chip");
        const moods = getSelectedValues(".mood-chip");
        const styles = getSelectedValues(".style-chip");
        const extra = customNote ? customNote.value.trim() : "";

        let prompt = `Je veux des recommandations cohérentes avec mes séries préférées.
Réponds en français.
Propose 5 séries maximum.
Pour chaque suggestion, donne :
- le nom de la série
- le genre principal
- une explication courte et claire
- pourquoi elle correspond à mes goûts.`;

        if (genres.length > 0) {
            prompt += `\n\nGenres souhaités : ${genres.join(", ")}.`;
        }

        if (moods.length > 0) {
            prompt += `\nAmbiance recherchée : ${moods.join(", ")}.`;
        }

        if (styles.length > 0) {
            prompt += `\nÉléments importants : ${styles.join(", ")}.`;
        }

        if (extra) {
            prompt += `\nContraintes ou préférences supplémentaires : ${extra}`;
        }

        if (promptInput) {
            promptInput.value = prompt;
        }
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