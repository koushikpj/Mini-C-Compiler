const examples = {
  valid: `int x;
float y = 10.5;
int list[10];

x = 5 + 3 * 2;

if (x > 10) {
    print(x);
} else {
    print(y);
}

while (x < 20) {
    x = x + 1;
}
`,
  semantic: `int x;
float y;

x = 2.5;
z = x + 1;
print(y);
`,
  lexical: `int x;
x = 10 @ 2;
`,
};

const STAGE_LIST = ["output", "all", "tokens", "ast", "symbols", "tac"];

const source = document.querySelector("#source");
const output = document.querySelector("#output");
const statusBox = document.querySelector("#status");
const runButton = document.querySelector("#run");
const clearOutput = document.querySelector("#clearOutput");
const stages = Array.from(document.querySelectorAll(".stage"));

let selectedStage = "all";

// Cache holds the result for each stage after a Run
let cache = {};

function setStatus(text, isError = false) {
  statusBox.textContent = text;
  statusBox.classList.toggle("error", isError);
}

function showCachedStage() {
  if (Object.keys(cache).length === 0) return;

  if (cache.error) {
    output.textContent = "✖  " + cache.error;
    return;
  }

  const content = cache[selectedStage];
  if (content !== undefined) {
    output.textContent = content;
  }
}

function setStage(stage) {
  selectedStage = stage;
  stages.forEach((button) => {
    button.classList.toggle("active", button.dataset.stage === stage);
  });
  showCachedStage();
}

async function runCompiler() {
  setStatus("Running…");
  output.textContent = "Compiling…";
  cache = {};

  try {
    // Fetch every stage in parallel so tab switching is instant
    const fetches = {};
    for (const stage of STAGE_LIST) {
      fetches[stage] = fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: source.value, stage }),
      }).then((r) => r.json());
    }

    const results = {};
    let hasError = false;

    for (const stage of Object.keys(fetches)) {
      results[stage] = await fetches[stage];
      if (!results[stage].ok) hasError = true;
    }

    if (hasError) {
      // Use the "all" response for the error message
      const errMsg = results["all"].output || "Compilation failed.";
      cache = { error: errMsg };
      // Fill every tab with the error so switching works
      for (const s of STAGE_LIST) {
        cache[s] = "✖  " + errMsg;
      }
      setStatus("Error", true);
    } else {
      for (const stage of STAGE_LIST) {
        cache[stage] = results[stage].output || "";
      }
      setStatus("Success");
    }

    showCachedStage();
  } catch (error) {
    output.textContent = `Frontend error: ${error.message}`;
    setStatus("Error", true);
  }
}

document.querySelector("#loadValid").addEventListener("click", () => {
  source.value = examples.valid;
  setStatus("Ready");
});

document.querySelector("#loadSemantic").addEventListener("click", () => {
  source.value = examples.semantic;
  setStatus("Ready");
});

document.querySelector("#loadLexical").addEventListener("click", () => {
  source.value = examples.lexical;
  setStatus("Ready");
});

stages.forEach((button) => {
  button.addEventListener("click", () => setStage(button.dataset.stage));
});

runButton.addEventListener("click", runCompiler);

clearOutput.addEventListener("click", () => {
  output.textContent = "";
  cache = {};
  setStatus("Ready");
});

source.value = examples.valid;
