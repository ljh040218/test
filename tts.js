function speak(text) {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ko-KR';
  synth.speak(utterance);
}

export { speak };
