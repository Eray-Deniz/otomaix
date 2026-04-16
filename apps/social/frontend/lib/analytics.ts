/**
 * PostHog analytics wrapper — safe to call on server or without key.
 * Import `analytics` anywhere; if PostHog is not initialized it's a no-op.
 */
import posthog from 'posthog-js'

function safe(fn: () => void) {
  if (typeof window === 'undefined') return
  try {
    fn()
  } catch {
    // silently ignore analytics errors
  }
}

export const analytics = {
  // ─── Identity ───────────────────────────────────────────────────────────────
  identify(userId: string, properties?: Record<string, unknown>) {
    safe(() => posthog.identify(userId, properties))
  },
  reset() {
    safe(() => posthog.reset())
  },

  // ─── Generic capture ────────────────────────────────────────────────────────
  capture(event: string, properties?: Record<string, unknown>) {
    safe(() => posthog.capture(event, properties))
  },

  // ─── Onboarding funnel ──────────────────────────────────────────────────────
  onboardingStarted() {
    safe(() => posthog.capture('onboarding_started'))
  },
  onboardingStepCompleted(step: number) {
    safe(() => posthog.capture('onboarding_step_completed', { step }))
  },
  onboardingCompleted() {
    safe(() => posthog.capture('onboarding_completed'))
  },
  onboardingSkipped(atStep: number) {
    safe(() => posthog.capture('onboarding_skipped', { at_step: atStep }))
  },

  // ─── Content creation ───────────────────────────────────────────────────────
  contentCreationStarted(contentType: string) {
    safe(() => posthog.capture('content_creation_started', { content_type: contentType }))
  },
  ideaSuggestionUsed() {
    safe(() => posthog.capture('idea_suggestion_used'))
  },
  documentReferenceUsed(count: number) {
    safe(() => posthog.capture('document_reference_used', { doc_count: count }))
  },
  contentGenerated(contentType: string, generationTimeSeconds?: number) {
    safe(() =>
      posthog.capture('content_generated', {
        content_type: contentType,
        generation_time_seconds: generationTimeSeconds,
      })
    )
  },
  contentPublished(platform: string) {
    safe(() => posthog.capture('content_published', { platform }))
  },
  contentScheduled() {
    safe(() => posthog.capture('content_scheduled'))
  },

  // ─── Feature adoption ───────────────────────────────────────────────────────
  calendarOpened() {
    safe(() => posthog.capture('calendar_opened'))
  },
  autopostingConfigured() {
    safe(() => posthog.capture('autoposting_configured'))
  },
  competitorAdded() {
    safe(() => posthog.capture('competitor_added'))
  },
  trendPostCreated() {
    safe(() => posthog.capture('trend_post_created'))
  },
  trendLayerAViewed(sector?: string) {
    safe(() => posthog.capture('trend_layer_a_viewed', { sector }))
  },
  trendLayerBTriggered(sector?: string) {
    safe(() => posthog.capture('trend_layer_b_triggered', { sector }))
  },
  trendLayerCGenerated(sector?: string) {
    safe(() => posthog.capture('trend_layer_c_generated', { sector }))
  },
  trendQuotaExhausted(layer: string) {
    safe(() => posthog.capture('trend_quota_exhausted', { layer }))
  },
  trendPaywallShown(layer: string, currentPlan?: string) {
    safe(() => posthog.capture('trend_paywall_shown', { layer, current_plan: currentPlan }))
  },
  avatarCreated() {
    safe(() => posthog.capture('avatar_created'))
  },
  telegramApprovalEnabled() {
    safe(() => posthog.capture('telegram_approval_enabled'))
  },

  // ─── Conversion ─────────────────────────────────────────────────────────────
  pricingPageViewed() {
    safe(() => posthog.capture('pricing_page_viewed'))
  },
  planSelected(planId: string) {
    safe(() => posthog.capture('plan_selected', { plan_id: planId }))
  },
  checkoutStarted(planId: string) {
    safe(() => posthog.capture('checkout_started', { plan_id: planId }))
  },
}
