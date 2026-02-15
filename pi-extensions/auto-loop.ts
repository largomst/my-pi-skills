/**
 * Auto Loop Extension
 *
 * Automatically activates loop on first user input, eliminating the need
 * to manually type /loop each time. Works by injecting the loop prompt
 * after the first agent turn completes.
 */

import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";

export default function autoLoopExtension(pi: ExtensionAPI) {
	// Configuration state
	let autoLoopEnabled = true;
	let firstAgentTurn = true;

	/**
	 * Update the TUI widget to show auto-loop status
	 */
	function updateWidget(ctx: ExtensionContext): void {
		if (!ctx.hasUI) return;

		if (!autoLoopEnabled) {
			// Clear widget when disabled
			ctx.ui.setWidget("aloop", undefined);
			return;
		}

		// Show status in the widget
		const status = firstAgentTurn ? "ready" : "active";
		const text = `Auto-loop: ${status}`;
		ctx.ui.setWidget("aloop", [ctx.ui.theme.fg("muted", text)]);
	}

	/**
	 * Register the /aloop command to control auto-loop behavior
	 *
	 * Usage:
	 *   /aloop        - Show current status
	 *   /aloop on     - Enable auto-loop
	 *   /aloop off    - Disable auto-loop
	 */
	pi.registerCommand("aloop", {
		description: "Toggle auto-loop on/off (automatically activates loop on first input)",
		handler: async (args, ctx) => {
			if (args === "on") {
				autoLoopEnabled = true;
				firstAgentTurn = true; // Reset to trigger on next input
				updateWidget(ctx);
				ctx.ui.notify("Auto-loop: ON", "info");
			} else if (args === "off") {
				autoLoopEnabled = false;
				updateWidget(ctx);
				ctx.ui.notify("Auto-loop: OFF", "info");
			} else {
				// Show current status
				const status = autoLoopEnabled ? "ON" : "OFF";
				ctx.ui.notify(`Auto-loop is ${status}`, "info");
			}
		},
	});

	/**
	 * Automatically activate loop after first agent turn
	 *
	 * This triggers after the LLM completes processing the first user message,
	 * injecting the loop prompt as a follow-up message.
	 */
	pi.on("agent_end", async (_event, ctx) => {
		if (!autoLoopEnabled || !firstAgentTurn) {
			return;
		}

		firstAgentTurn = false;

		// Inject the loop prompt as a custom message
		// This will be processed by the loop.ts extension
		pi.sendMessage({
			customType: "loop",
			content: "Continue until you are done. When finished, call the signal_loop_success tool.",
			display: true,
			details: {
				active: true,
				mode: "self",
				prompt: "Continue until you are done. When finished, call the signal_loop_success tool.",
				summary: "done",
				loopCount: 1,
			},
		}, {
			deliverAs: "followUp",
			triggerTurn: true,
		});

		updateWidget(ctx);
	});

	/**
	 * Reset firstAgentTurn flag on new session
	 * Allows auto-loop to trigger again when starting fresh
	 */
	pi.on("session_start", async (_event, ctx) => {
		firstAgentTurn = true;
		updateWidget(ctx);
	});

	/**
	 * Reset firstAgentTurn flag when switching sessions
	 */
	pi.on("session_switch", async (_event, ctx) => {
		firstAgentTurn = true;
		updateWidget(ctx);
	});
}
