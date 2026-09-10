import { onRequestGet as __api_lead_js_onRequestGet } from "/Users/nishant/Vibe/cielo-website/functions/api/lead.js"
import { onRequestPost as __api_lead_js_onRequestPost } from "/Users/nishant/Vibe/cielo-website/functions/api/lead.js"

export const routes = [
    {
      routePath: "/api/lead",
      mountPath: "/api",
      method: "GET",
      middlewares: [],
      modules: [__api_lead_js_onRequestGet],
    },
  {
      routePath: "/api/lead",
      mountPath: "/api",
      method: "POST",
      middlewares: [],
      modules: [__api_lead_js_onRequestPost],
    },
  ]