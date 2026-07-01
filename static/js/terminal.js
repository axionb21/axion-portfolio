document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("terminal-toggle");
  const body = document.getElementById("terminal-body");
  const output = document.getElementById("terminal-output");
  const input = document.getElementById("terminal-input");

  if (!toggle) return;

  toggle.addEventListener("click", () => {
    body.classList.toggle("open");
    if (body.classList.contains("open")) input.focus();
  });

  function printLine(text, isPrompt = false) {
    const div = document.createElement("div");
    if (isPrompt) div.className = "line-prompt";
    div.textContent = text;
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
  }

  printLine("root@axion:~$ type 'help' to see available commands");

  input.addEventListener("keydown", async (e) => {
    if (e.key !== "Enter") return;
    const cmd = input.value.trim();
    if (!cmd) return;
    printLine(`root@axion:~$ ${cmd}`, true);
    input.value = "";

    if (cmd === "clear") {
      output.innerHTML = "";
      return;
    }

    try {
      const res = await fetch("/api/terminal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd }),
      });
      const data = await res.json();
      if (data.redirect) {
        printLine(`redirecting to ${data.redirect} ...`);
        setTimeout(() => (window.location.href = data.redirect), 400);
      } else {
        printLine(data.output || "");
      }
    } catch (err) {
      printLine("error: could not reach server");
    }
  });
});
