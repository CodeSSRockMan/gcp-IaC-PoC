resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account_id
  display_name    = "Project Budget"
  amount {
    specified_amount {
      currency_code = "USD"
      units         = 10
    }
  }
  budget_filter {
    projects = ["projects/${var.project_id}"]
  }
  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.9
  }
  threshold_rules {
    threshold_percent = 1.0
  }
}
