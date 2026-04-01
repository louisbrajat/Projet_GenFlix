document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("gemini-btn");
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("gemini-result");
    const resultText = document.getElementById("gemini-text");
    const promptInput = document.getElementById("prompt-input");
    const seriesCards = document.querySelectorAll(".serie-item");

    button.addEventListener("click", async () => {
        const prompt = promptInput.value.trim();

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

        loading.classList.remove("hidden");
        resultBox.classList.add("hidden");
        resultText.textContent = "";

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
                resultText.textContent = data.error || "Erreur lors de la génération.";
            } else {
                resultText.textContent = data.result;
            }

            resultBox.classList.remove("hidden");
        } catch (error) {
            resultText.textContent = "Erreur de connexion au serveur.";
            resultBox.classList.remove("hidden");
        } finally {
            loading.classList.add("hidden");
        }
    });
});