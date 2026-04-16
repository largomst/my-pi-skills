/**
 * Auto-Compact Extension for Pi Coding Agent
 * 
 * Automatically triggers context compaction when usage reaches a configurable threshold.
 * After compaction completes, sends a "Continue" message to resume task execution.
 * 
 * Features:
 * - Percentage-based threshold (default 40%)
 * - Prevents duplicate triggers during compaction
 * - Minimum interval between compactions (5 minutes)
 * - Manual trigger command: /auto-compact [custom instructions]
 * - Custom instructions for compression
 * - Automatic task continuation after compaction
 * 
 * Usage:
 *   pi -e ./auto-compact.ts
 *   
 * Or install to:
 *   - Global: ~/.pi/agent/extensions/auto-compact.ts
 *   - Project: .pi/extensions/auto-compact.ts
 */

import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";

// ============= Configuration =============
const COMPACT_THRESHOLD_PERCENT = 40;        // Trigger at 40% (change as needed)
const MIN_INTERVAL_MS = 5 * 60 * 1000;       // 5 minutes between compactions
const CUSTOM_INSTRUCTIONS = 
    "Summarize the conversation preserving: " +
    "1. Main goals and objectives " +
    "2. Key technical decisions and rationale " +
    "3. Code changes and file operations " +
    "4. Current task progress and next steps " +
    "5. Any blockers or open questions. " +
    "Keep enough detail to continue working seamlessly.";

export default function (pi: ExtensionAPI) {
    let isCompacting = false;
    let lastCompactionTime = 0;

    const triggerCompaction = (pi: ExtensionAPI, ctx: ExtensionContext, customInstructions?: string) => {
        if (isCompacting) {
            if (ctx.hasUI) {
                ctx.ui.notify("Compaction already in progress", "warning");
            }
            return;
        }

        const instructions = customInstructions || CUSTOM_INSTRUCTIONS;
        
        if (ctx.hasUI) {
            ctx.ui.notify(`Starting compaction (threshold: ${COMPACT_THRESHOLD_PERCENT}%)`, "info");
        }

        isCompacting = true;
        
        ctx.compact({
            customInstructions: instructions,
            onComplete: (result) => {
                isCompacting = false;
                lastCompactionTime = Date.now();
                
                if (ctx.hasUI) {
                    ctx.ui.notify("✓ Compaction completed, continuing task...", "success");
                }
                
                // Send continue message to resume task execution
                pi.sendUserMessage("Continue", { deliverAs: "followUp" });
            },
            onError: (error) => {
                isCompacting = false;
                
                if (ctx.hasUI) {
                    ctx.ui.notify(`✗ Compaction failed: ${error.message}`, "error");
                }
            },
        });
    };

    // Monitor context usage at the end of each turn
    pi.on("turn_end", (_event, ctx) => {
        const usage = ctx.getContextUsage();
        
        // Skip if usage info not available (e.g., right after compaction)
        if (!usage || usage.percent === null) {
            return;
        }

        // Skip if already compacting
        if (isCompacting) {
            return;
        }

        // Skip if too recent (prevent rapid-fire compactions)
        if (lastCompactionTime && (Date.now() - lastCompactionTime) < MIN_INTERVAL_MS) {
            return;
        }

        // Check threshold and trigger if exceeded
        if (usage.percent >= COMPACT_THRESHOLD_PERCENT) {
            if (ctx.hasUI) {
                ctx.ui.notify(
                    `⚠ Context usage: ${usage.percent.toFixed(1)}% (threshold: ${COMPACT_THRESHOLD_PERCENT}%)`,
                    "info"
                );
            }
            triggerCompaction(pi, ctx);
        }
    });

    // Manual trigger command
    pi.registerCommand("auto-compact", {
        description: `Trigger compaction immediately (auto threshold: ${COMPACT_THRESHOLD_PERCENT}%)`,
        handler: async (args, ctx) => {
            const instructions = args.trim() || undefined;
            triggerCompaction(pi, ctx, instructions);
        },
    });

    // Clear status on shutdown
    pi.on("session_shutdown", () => {
        isCompacting = false;
        lastCompactionTime = 0;
    });
}
