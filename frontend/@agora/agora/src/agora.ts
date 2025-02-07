interface PollingOptions<T> {
	initialDelayMs?: number;
	maxDelayMs?: number;
	maxDurationMs?: number;
	shouldContinue: (response: T) => boolean;
}

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
