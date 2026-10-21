const toggle = document.querySelector('#script-toggle');
const script = document.querySelector('#script-text');
const copyButton = document.querySelector('#copy-script');
const copyStatus = document.querySelector('#copy-status');

toggle?.addEventListener('click', () => {
  const expanded = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!expanded));
  script.hidden = expanded;
  toggle.textContent = expanded ? '台本を表示' : '台本を閉じる';
});

copyButton?.addEventListener('click', async () => {
  const text = Array.from(script.querySelectorAll('.script-line'))
    .map(line => `${line.querySelector('.speaker').textContent}\n${line.querySelector('p').textContent}`)
    .join('\n\n');
  try {
    await navigator.clipboard.writeText(text);
    copyStatus.textContent = '台本をコピーしました。';
  } catch {
    copyStatus.textContent = 'コピーできませんでした。台本を表示して手動で選択してください。';
  }
});
