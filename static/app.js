(() => {
  const form = document.getElementById("collatz-form");
  if (!form) {
    return;
  }

  const numberInput = document.getElementById("number");
  const submitButton = form.querySelector('button[type="submit"]');
  const errorMessage = document.getElementById("error-message");
  const successMessage = document.getElementById("success-message");
  const warningMessage = document.getElementById("warning-message");
  const tableSection = document.getElementById("table-section");
  const tableBody = document.getElementById("sequence-body");
  const chartSection = document.getElementById("chart-section");
  const chartContainer = document.getElementById("chart");
  const maxSteps = window.CollatzConfig?.maxSteps ?? 1000;

  let currentDisplayId = 0;

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function clearMessages() {
    if (errorMessage) {
      errorMessage.textContent = "";
      errorMessage.hidden = true;
    }

    if (successMessage) {
      successMessage.textContent = "";
      successMessage.hidden = true;
    }

    if (warningMessage) {
      warningMessage.textContent = "";
      warningMessage.hidden = true;
    }
  }

  function showError(message) {
    if (!errorMessage) {
      return;
    }

    errorMessage.textContent = message;
    errorMessage.hidden = false;
  }

  function showSuccess(message) {
    if (!successMessage) {
      return;
    }

    successMessage.textContent = message;
    successMessage.hidden = false;
  }

  function showWarning(message) {
    if (!warningMessage) {
      return;
    }

    warningMessage.textContent = message;
    warningMessage.hidden = false;
  }

  function resetView() {
    if (tableBody) {
      tableBody.innerHTML = "";
    }

    if (chartContainer) {
      chartContainer.innerHTML = "";
    }

    if (tableSection) {
      tableSection.hidden = true;
    }

    if (chartSection) {
      chartSection.hidden = true;
    }
  }

  function setLoadingState(isLoading) {
    if (!submitButton) {
      return;
    }

    submitButton.disabled = isLoading;
    submitButton.textContent = isLoading ? "計算中…" : "計算する";
  }

  function appendRow(step) {
    if (!tableBody) {
      return;
    }

    const row = document.createElement("tr");

    const stepCell = document.createElement("td");
    stepCell.dataset.label = "ステップ";
    stepCell.textContent = String(step.step);

    const valueCell = document.createElement("td");
    valueCell.dataset.label = "値";
    valueCell.textContent = String(step.value);

    const operationCell = document.createElement("td");
    operationCell.dataset.label = "操作";
    operationCell.textContent = step.operation;

    row.append(stepCell, valueCell, operationCell);
    tableBody.appendChild(row);
  }

  function appendBar(step, maxValue) {
    if (!chartContainer) {
      return;
    }

    const normalizedMax = maxValue === 0 ? 1 : maxValue;
    const height = Math.round((step.value / normalizedMax) * 100);

    const bar = document.createElement("div");
    bar.className = "chart-bar";
    bar.style.height = `${height}%`;

    const value = document.createElement("span");
    value.className = "chart-value";
    value.textContent = String(step.value);

    const stepLabel = document.createElement("span");
    stepLabel.className = "chart-step";
    stepLabel.textContent = `#${step.step}`;

    bar.append(value, stepLabel);
    chartContainer.appendChild(bar);
  }

  async function displaySequence(steps, truncated, displayId) {
    if (!Array.isArray(steps) || steps.length === 0) {
      showError("結果を表示できませんでした。");
      return;
    }

    const totalSteps = steps.length;
    const computedSteps = Math.max(totalSteps - 1, 0);
    const maxValue = steps.reduce(
      (currentMax, step) => Math.max(currentMax, step.value),
      0,
    );

    if (tableSection) {
      tableSection.hidden = false;
    }

    if (chartSection) {
      chartSection.hidden = false;
    }

    for (let index = 0; index < steps.length; index += 1) {
      if (displayId !== currentDisplayId) {
        return;
      }

      if (index > 0) {
        await delay(1000);
        if (displayId !== currentDisplayId) {
          return;
        }
      }

      const step = steps[index];
      appendRow(step);
      appendBar(step, maxValue);

      if (successMessage) {
        if (computedSteps > 0) {
          const progress = Math.min(step.step, computedSteps);
          showSuccess(`計算中…（${progress}/${computedSteps}）`);
        } else {
          showSuccess("計算中…");
        }
      }
    }

    if (displayId !== currentDisplayId) {
      return;
    }

    showSuccess(
      `計算したステップ数: ${computedSteps} （開始値を含めた合計 ${totalSteps} 件）`,
    );

    if (truncated) {
      showWarning(`上限 ${maxSteps} ステップに達したため途中で停止しました。`);
    } else if (warningMessage) {
      warningMessage.hidden = true;
      warningMessage.textContent = "";
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();

    const value = numberInput?.value.trim();
    if (!value) {
      showError("値を入力してください。");
      return;
    }

    const number = Number(value);
    if (!Number.isInteger(number) || number < 1) {
      showError("1 以上の整数を入力してください。");
      return;
    }

    currentDisplayId += 1;
    const displayId = currentDisplayId;
    resetView();
    setLoadingState(true);

    try {
      const response = await fetch("/api/collatz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const message = data && typeof data.error === "string"
          ? data.error
          : "計算に失敗しました。";
        showError(message);
        return;
      }

      if (!data) {
        showError("サーバーからの応答を解析できませんでした。");
        return;
      }

      setLoadingState(false);
      showSuccess("計算を開始します…");
      await displaySequence(data.steps, data.truncated, displayId);
    } catch (error) {
      console.error(error);
      showError("ネットワークエラーが発生しました。");
    } finally {
      if (displayId === currentDisplayId) {
        setLoadingState(false);
      }
    }
  });
})();
