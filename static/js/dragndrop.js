document.addEventListener("DOMContentLoaded", function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    async function postData(url, data) {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify(data)
            });
            console.log(response)

            if (!response.ok) {
                console.error("Request failed:", response.status, await response.text());
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    }

    new Sortable(document.getElementById("lists-scroll"), {
        animation: 150,
        handle: ".card-header",
        draggable: ".card-list:not(.no-drag)",
        onEnd: () => {
            let order = [];
            document.querySelectorAll(".card-list:not(.no-drag)").forEach((el, index) => {
                if (el.dataset.listId) {
                    order.push({ id: el.dataset.listId, position: index });
                }
            });
            postData(window.updateListOrderUrl, { order });
        }
    });

    document.querySelectorAll(".task-list").forEach(el => {
        new Sortable(el, {
            group: "tasks",
            animation: 150,
            draggable: ".task-item",
            onEnd: () => {
                let moves = [];
                document.querySelectorAll(".task-list").forEach(listEl => {
                    let listId = listEl.dataset.listId;
                    listEl.querySelectorAll(".task-item").forEach((taskEl, index) => {
                        moves.push({
                            id: taskEl.dataset.taskId,
                            list: listId,
                            position: index
                        });
                    });
                });
                postData(window.updateTaskOrderUrl, { moves });
            }
        });
    });
});
