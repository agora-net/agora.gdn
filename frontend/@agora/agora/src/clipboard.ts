declare global {
	interface Window {
		copyToClipboard: typeof copyToClipboard;
	}
}

export const copyToClipboard = (btn: HTMLButtonElement, elementId: string) => {
	const element = document.getElementById(elementId);
	if (!element) return;

	const originalText = btn.textContent;
	const input = element as HTMLInputElement;

	const text = input.value || (input.textContent ?? "");
	navigator.clipboard
		.writeText(text)
		.then(() => {
			btn.classList.add("btn-success");
			btn.textContent = "Copied!";

			setTimeout(() => {
				btn.textContent = originalText;
				btn.classList.remove("btn-success");
			}, 1000);
		})
		.catch((err) => {
			console.error("Failed to copy:", err);
		});
};
window.copyToClipboard = copyToClipboard;
