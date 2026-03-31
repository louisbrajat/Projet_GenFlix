document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("gemini-btn");
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("gemini-result");
    const resultText = document.getElementById("gemini-text");

    button.addEventListener("click", async () => {
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
                    last_series: [
                        "Breaking Bad",
                        "Dark",
                        "Lupin",
                        "Stranger Things",
                        "You",
                        "Elite",
                        "Narcos",
                        "Peaky Blinders",
                        "Vikings",
                        "The Witcher"
                    ]
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