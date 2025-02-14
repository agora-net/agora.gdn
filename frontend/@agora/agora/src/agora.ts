import Identicon, { type IdenticonOptions } from "identicon.js";

declare global {
	interface Window {
		pollWithBackoff: typeof pollWithBackoff;
	}
}

export interface PollingOptions<T> {
	initialDelayMs?: number;
	maxDelayMs?: number;
	maxDurationMs?: number;
	shouldContinue: (response: T) => boolean;
}

/**
/**
 * Example usage
 *     const result = await pollWithBackoff<{status: string}>(
	   'https://api.example.com/status',
	   {
		 shouldContinue: (data) => data.status === 'pending'
	   }
	 );
 *
 */
export const pollWithBackoff = async <T>(
	url: string,
	options: PollingOptions<T>,
): Promise<T> => {
	const start = Date.now();
	const {
		initialDelayMs = 1_000,
		maxDelayMs = 1000 * 60 * 5, // 5 minutes
		maxDurationMs = 1000 * 60 * 10, // 10 minutes
		shouldContinue,
	} = options;

	let currentDelay = initialDelayMs;

	while (true) {
		try {
			const response = await fetch(url);
			const data = (await response.json()) as T;

			if (!shouldContinue(data)) {
				return data;
			}

			if (Date.now() - start > maxDurationMs) {
				throw new Error("Polling timed out");
			}

			// Add jitter to prevent thundering herd
			const jitter = Math.random() * 100;
			await new Promise((resolve) =>
				setTimeout(resolve, currentDelay + jitter),
			);

			// Exponential backoff with max delay cap
			currentDelay = Math.min(currentDelay * 2, maxDelayMs);
		} catch (error) {
			throw new Error(`Polling failed: ${error}`);
		}
	}
};

window.pollWithBackoff = pollWithBackoff;

document.addEventListener("DOMContentLoaded", async () => {
	// Find all elements with the data-identicon attribute
	const elements = document.querySelectorAll("[data-identicon]");
	const options: IdenticonOptions = {
		foreground: [255, 255, 255, 255],
		background: [0, 0, 0, 255],
		margin: 0.2,
		size: 128,
		format: "svg",
	};
	// for each one extract the data value and create an identicon
	for (const element of elements) {
		const data = element.getAttribute("data-identicon");
		if (data) {
			const identicon = new Identicon(data, options);
			// insert the identicon as an img
			const img = document.createElement("img");
			img.src = `data:image/svg+xml;base64,${identicon.toString()}`;
			element.appendChild(img);
		}
	}
});
