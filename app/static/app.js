const state = {
  testId: null,
  currentItem: null,
  theta: null,
  se: null,
  listening: null,
  finished: false,
  pauseDomain: null,
  timerStartedAt: null,
  timerInterval: null,
};

const startForm = document.getElementById('start-form');
const startPanel = document.getElementById('start-panel');
const startStatus = document.getElementById('start-status');
const pausePanel = document.getElementById('pause-panel');
const pauseTitle = document.getElementById('pause-title');
const pauseMessage = document.getElementById('pause-message');
const resumeButton = document.getElementById('resume-section');
const questionPanel = document.getElementById('question-panel');
const questionDomain = document.getElementById('question-domain');
const questionMetadata = document.getElementById('question-metadata');
const itemStem = document.getElementById('item-stem');
const answerForm = document.getElementById('answer-form');
const submitAnswerBtn = document.getElementById('submit-answer');
const finishBtn = document.getElementById('finish-test');
const answerStatus = document.getElementById('answer-status');
const thetaValue = document.getElementById('theta-value');
const seValue = document.getElementById('se-value');
const timerDisplay = document.getElementById('timer-display');
const reportPanel = document.getElementById('report-panel');
const reportSummary = document.getElementById('report-summary');
const reportTable = document.getElementById('report-table');
const reportTableBody = reportTable.querySelector('tbody');
const restartBtn = document.getElementById('restart');
const listeningContainer = document.getElementById('listening-container');
let listeningAudio = document.getElementById('listening-audio');
const playCounter = document.getElementById('play-counter');

resumeButton.addEventListener('click', async () => {
  if (!state.testId) return;
  resumeButton.disabled = true;
  try {
    const response = await fetch(`/api/test/${state.testId}/resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'Unable to resume section');
    }
    await fetchNextItem();
  } catch (error) {
    pauseMessage.textContent = error.message;
  } finally {
    resumeButton.disabled = false;
  }
});

startForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (state.testId) {
    await resetUI();
  }
  const formData = new FormData(startForm);
  const level = formData.get('start-level');
  const firstName = formData.get('first-name');
  const lastName = formData.get('last-name');
  startStatus.textContent = 'Starting adaptive session…';
  try {
    const response = await fetch('/api/test/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_level: level,
        first_name: firstName,
        last_name: lastName,
      }),
    });
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'Failed to start test');
    }
    const data = await response.json();
    state.testId = data.test_id;
    state.theta = data.theta;
    state.se = data.se;
    state.timerStartedAt = Date.now();
    startTimer();
    startStatus.textContent = 'Session ready. Take a pause before the first section.';
    state.pauseDomain = data.upcoming_part;
    showPanel(pausePanel);
    updatePauseMessage(data.upcoming_part);
    updateProgress();
    await fetchNextItem();
  } catch (error) {
    console.error(error);
    startStatus.textContent = error.message;
  }
});

async function fetchNextItem() {
  if (!state.testId) return;
  try {
    const response = await fetch(`/api/test/${state.testId}/next`);
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'No more items available');
    }
    const item = await response.json();
    if (item.pause) {
      state.pauseDomain = item.domain;
      updatePauseMessage(item.domain, item.questions);
      showPanel(pausePanel);
      answerStatus.textContent = '';
      return;
    }
    state.currentItem = item;
    showPanel(questionPanel);
    renderItem(item);
    answerStatus.textContent = '';
  } catch (error) {
    if (!state.finished) {
      await finishTest();
    }
  }
}

function renderItem(item) {
  questionDomain.textContent = `${capitalize(item.domain)} Question`;
  const metaBits = [];
  if (item.metadata?.topic) metaBits.push(item.metadata.topic);
  if (item.metadata?.difficulty) metaBits.push(`Difficulty: ${item.metadata.difficulty}`);
  questionMetadata.textContent = metaBits.join(' • ');
  itemStem.textContent = item.stem;

  buildOptions(item);
  setupListening(item);
}

function buildOptions(item) {
  answerForm.innerHTML = '';
  submitAnswerBtn.disabled = true;
  const isMulti = item.model.toLowerCase() === 'gpcm';
  const inputType = isMulti ? 'checkbox' : 'radio';

  item.options.forEach((option, index) => {
    const row = document.createElement('label');
    row.className = 'option-row';

    const input = document.createElement('input');
    input.type = inputType;
    input.name = 'answer';
    input.value = index;

    input.addEventListener('change', () => {
      updateSelectionState(isMulti);
    });

    const text = document.createElement('span');
    text.textContent = option;

    row.appendChild(input);
    row.appendChild(text);
    answerForm.appendChild(row);
  });
}

function updateSelectionState(isMulti) {
  const inputs = Array.from(answerForm.querySelectorAll('input'));
  const selected = inputs.filter((input) => input.checked);
  submitAnswerBtn.disabled = selected.length === 0;
  inputs.forEach((input) => {
    input.parentElement.classList.toggle('selected', input.checked);
  });
  if (!isMulti) {
    inputs.forEach((input) => {
      if (!input.checked) input.parentElement.classList.remove('selected');
    });
  }
}

function setupListening(item) {
  if (item.domain !== 'listening' || !item.metadata?.audio_url) {
    listeningContainer.classList.add('hidden');
    listeningAudio.pause();
    listeningAudio.removeAttribute('src');
    state.listening = null;
    return;
  }

  const freshAudio = listeningAudio.cloneNode(true);
  listeningAudio.parentNode.replaceChild(freshAudio, listeningAudio);
  listeningAudio = freshAudio;

  state.listening = {
    itemId: item.item_id,
    plays: 0,
    max: item.max_plays || 2,
    pending: false,
    blocked: false,
  };

  listeningAudio.src = item.metadata.audio_url;
  listeningAudio.load();
  playCounter.textContent = `Plays: 0 / ${state.listening.max}`;
  listeningContainer.classList.remove('hidden');

  listeningAudio.addEventListener('play', async () => {
    if (!state.listening || state.listening.blocked) {
      listeningAudio.pause();
      return;
    }
    if (state.listening.pending) return;
    if (state.listening.plays >= state.listening.max) {
      listeningAudio.pause();
      listeningAudio.currentTime = 0;
      return;
    }
    state.listening.pending = true;
    try {
      const response = await fetch(`/api/test/${state.testId}/play`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: state.currentItem.item_id }),
      });
      if (!response.ok) {
        throw new Error((await response.json()).detail || 'Play limit reached');
      }
      const data = await response.json();
      state.listening.plays = data.plays;
      playCounter.textContent = `Plays: ${data.plays} / ${data.max_plays}`;
      if (data.plays >= data.max_plays) {
        playCounter.textContent += ' • Limit reached';
      }
    } catch (error) {
      state.listening.blocked = true;
      answerStatus.textContent = error.message;
      listeningAudio.pause();
      listeningAudio.currentTime = 0;
    } finally {
      state.listening.pending = false;
    }
  });
}

submitAnswerBtn.addEventListener('click', async () => {
  if (!state.currentItem) return;
  const inputs = Array.from(answerForm.querySelectorAll('input:checked'));
  if (inputs.length === 0) return;
  const payload = buildAnswerPayload(inputs);
  submitAnswerBtn.disabled = true;
  answerStatus.textContent = 'Scoring response…';

  try {
    const response = await fetch(`/api/test/${state.testId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'Unable to submit answer');
    }
    const data = await response.json();
    state.theta = data.theta;
    state.se = data.se;
    const correct = data.correct ? 'correct' : 'incorrect';
    answerStatus.textContent = `Answer ${correct}. θ = ${state.theta.toFixed(2)} • SE = ${state.se.toFixed(2)}`;
    updateProgress();

    if (data.next_part === null || data.next_part === undefined) {
      await finishTest();
      return;
    }
    await fetchNextItem();
  } catch (error) {
    console.error(error);
    answerStatus.textContent = error.message;
  }
});

function buildAnswerPayload(inputs) {
  const answerValues = inputs.map((input) => Number.parseInt(input.value, 10));
  const isMulti = state.currentItem.model.toLowerCase() === 'gpcm';
  return {
    item_id: state.currentItem.item_id,
    response: { answer: isMulti ? answerValues : answerValues[0] },
  };
}

finishBtn.addEventListener('click', async () => {
  await finishTest();
});

async function finishTest() {
  if (!state.testId || state.finished) return;
  try {
    const response = await fetch(`/api/test/${state.testId}/finish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm: true }),
    });
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'Unable to finish test');
    }
    const data = await response.json();
    state.theta = data.theta;
    state.se = data.se;
    state.finished = true;
    stopTimer();
    updateProgress();
    await loadReport();
  } catch (error) {
    console.error(error);
    answerStatus.textContent = error.message;
  }
}

async function loadReport() {
  if (!state.testId) return;
  try {
    const response = await fetch(`/api/report/${state.testId}`);
    if (!response.ok) {
      throw new Error((await response.json()).detail || 'Unable to load report');
    }
    const data = await response.json();
    showPanel(reportPanel);
    reportSummary.innerHTML = `
      <p><strong>θ:</strong> ${data.theta.toFixed(2)} • <strong>SE:</strong> ${data.se.toFixed(2)} • <strong>T-score:</strong> ${data.t_score.toFixed(1)}</p>
      <p><strong>CEFR level:</strong> ${data.cefr}</p>
    `;
    reportTableBody.innerHTML = '';
    if (Array.isArray(data.domains) && data.domains.length > 0) {
      data.domains.forEach((domain) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${capitalize(domain.domain)}</td>
          <td>${domain.average_score.toFixed(2)}</td>
          <td>${domain.cefr}</td>
        `;
        reportTableBody.appendChild(row);
      });
      reportTable.classList.remove('hidden');
    } else {
      reportTable.classList.add('hidden');
    }
  } catch (error) {
    reportSummary.textContent = error.message;
  }
}

restartBtn.addEventListener('click', async () => {
  await resetUI();
  startStatus.textContent = '';
  showPanel(startPanel);
});

async function resetUI() {
  state.testId = null;
  state.currentItem = null;
  state.theta = null;
  state.se = null;
  state.finished = false;
  state.listening = null;
  state.pauseDomain = null;
  stopTimer();
  state.timerStartedAt = null;
  answerForm.innerHTML = '';
  itemStem.textContent = 'Select start to begin.';
  questionMetadata.textContent = '';
  questionDomain.textContent = 'Vocabulary';
  answerStatus.textContent = '';
  thetaValue.textContent = 'θ = –';
  seValue.textContent = 'SE = –';
  timerDisplay.textContent = 'Elapsed 00:00';
  listeningContainer.classList.add('hidden');
  listeningAudio.pause();
  listeningAudio.removeAttribute('src');
  reportSummary.textContent = '';
  reportTableBody.innerHTML = '';
  reportTable.classList.add('hidden');
  submitAnswerBtn.disabled = true;
}

function updateProgress() {
  if (typeof state.theta === 'number') {
    thetaValue.textContent = `θ = ${state.theta.toFixed(2)}`;
  }
  if (typeof state.se === 'number') {
    seValue.textContent = `SE = ${state.se.toFixed(2)}`;
  }
}

function updatePauseMessage(domain, questions = 0) {
  if (!domain) {
    pauseTitle.textContent = 'Section pause';
    pauseMessage.textContent = 'Take a moment before moving to the next part of the test.';
    return;
  }
  const title = `${capitalize(domain)} section`;
  pauseTitle.textContent = title;
  const questionsInfo = questions > 0 ? ` (${questions} questions)` : '';
  pauseMessage.textContent = `Next up: ${capitalize(domain)}${questionsInfo}. Press “Start section” when you are ready.`;
}

function startTimer() {
  stopTimer();
  updateTimerDisplay();
  state.timerInterval = setInterval(updateTimerDisplay, 1000);
}

function stopTimer() {
  if (state.timerInterval) {
    clearInterval(state.timerInterval);
    state.timerInterval = null;
  }
}

function updateTimerDisplay() {
  if (!state.timerStartedAt) {
    timerDisplay.textContent = 'Elapsed 00:00';
    return;
  }
  const elapsedSeconds = Math.floor((Date.now() - state.timerStartedAt) / 1000);
  const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
  const seconds = String(elapsedSeconds % 60).padStart(2, '0');
  timerDisplay.textContent = `Elapsed ${minutes}:${seconds}`;
}

function showPanel(panel) {
  [startPanel, pausePanel, questionPanel, reportPanel].forEach((element) => {
    element.classList.toggle('hidden', element !== panel);
  });
}

function capitalize(value) {
  if (!value) return '';
  return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, ' ');
}
