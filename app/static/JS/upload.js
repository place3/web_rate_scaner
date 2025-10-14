// upload.js

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput");
  const startBtn = document.getElementById("startBtn");
  const clearBtn = document.getElementById("clearBtn");
  const filesListEl = document.getElementById("files-list");
  const sessionIdEl = document.getElementById("sessionId");

  let files = [];
  let sessionId = localStorage.getItem("scanner_session_id") || null;
  if (sessionId) sessionIdEl.textContent = sessionId;

  function renderFiles() {
    filesListEl.innerHTML = "";
    if (!files.length) {
      filesListEl.textContent = "Файлы не выбраны";
      return;
    }
    files.forEach((f, i) => {
      const row = document.createElement("div");
      row.className = "file-row";
      row.dataset.idx = i;

      row.innerHTML = `
        <div class="file-name">${f.name}</div>
        <div class="progress"><i></i></div>
        <div class="status">Ожидание</div>
      `;
      filesListEl.appendChild(row);
    });
  }

  fileInput.addEventListener("change", (e) => {
    files = Array.from(e.target.files);
    renderFiles();
  });

  clearBtn.addEventListener("click", () => {
    files = [];
    fileInput.value = null;
    renderFiles();
  });

  async function uploadFileXHR(file, session_id, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const form = new FormData();
      form.append("files", file);
      if (session_id) form.append("session_id", session_id);
      xhr.open("POST", "/upload", true);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) {
          const percent = Math.round((e.loaded / e.total) * 100);
          onProgress(percent);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const resp = JSON.parse(xhr.responseText);
            resolve(resp);
          } catch {
            reject(new Error("invalid json"));
          }
        } else reject(new Error("upload failed " + xhr.status));
      };
      xhr.onerror = () => reject(new Error("xhr error"));
      xhr.send(form);
    });
  }

  startBtn.addEventListener("click", async () => {
    if (!files.length) {
      alert("Выберите хотя бы один файл");
      return;
    }

    const concurrency = 3;
    let idx = 0;

    async function worker() {
      while (idx < files.length) {
        const cur = idx++;
        const file = files[cur];
        const row = document.querySelector(`.file-row[data-idx="${cur}"]`);
        const progBar = row.querySelector(".progress > i");
        const status = row.querySelector(".status");

        status.textContent = "Загрузка...";
        try {
          const resp = await uploadFileXHR(file, sessionId, (p) => {
            progBar.style.width = p + "%";
          });
          if (resp.session_id) {
            sessionId = resp.session_id;
            localStorage.setItem("scanner_session_id", sessionId);
            sessionIdEl.textContent = sessionId;
          }
          const info = resp.files && resp.files[0];
          status.textContent = info?.saved ? "Загружено" : "Ошибка: " + (info?.reason || "неизвестна");
        } catch (e) {
          status.textContent = "Ошибка: " + e.message;
        }
      }
    }

    await Promise.all(Array.from({ length: concurrency }, () => worker()));
    alert("Загрузка завершена. Session ID: " + (sessionId || "—"));
  });

  renderFiles();
});