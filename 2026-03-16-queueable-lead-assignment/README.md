# ☁️ Queueable Apex: Lead Assignment & Enrichment

![Apex](https://img.shields.io/badge/Salesforce-Apex-00A1E0?style=flat&logo=salesforce&logoColor=white)

> **Category**: Apex Class

## Overview

A Queueable Apex class that asynchronously enriches newly created Leads by making a REST callout to an external enrichment API and updating the Lead record with returned data. Demonstrates chaining Queueables.

## Files

```
2026-03-16-queueable-lead-assignment/
├── `LeadEnrichmentQueueable.cls`
├── `LeadEnrichmentQueueable_Test.cls`
```

## Code Preview

```java
/**
 * @description Queueable Apex that enriches Lead records asynchronously via
 *              an external REST API. Supports chaining for bulk enrichment.
 * @author      selvavp-hub
 */
public with sharing class LeadEnrichmentQueueable implements Queueable, Database.AllowsCallouts {

    private final List<Id> leadIds;
    private static final String API_ENDPOINT = 'https://api.enrichment.example.com/leads';

    public LeadEnrichmentQueueable(List<Id> leadIds) {
        this.leadIds = leadIds;
    }

    // ─── Queueable interface ──────────────────────────────────────────────────

    public void execute(QueueableContext ctx) {
        List<Lead> leads = [
            SELECT Id, Email, Company, Industry
            FROM Lead
            WHERE Id IN :leadIds AND IsConverted = false
        ];

        List<Lead> toUpdate = new List<Lead>();

        for (Lead lead : leads) {
            EnrichmentResult result = callEnrichmentAPI(lead.Email);
            if (result != null) {
                lead.Industry     = result.industry ?? lead.Industry;
                lead.Company      = result.companyName ?? lead.Company;
                lead.NumberOfEmployees = result.employeeCount;
                lead.Description  = 'Enriched via API on ' + Date.today().format();
                toUpdate.add(lead);
            }
        }

        if (!toUpdate.isEmpty()) {
            update toUpdate;
        }
    }
// ... (see full file)
```

## About

This project is part of [apex-lab](https://github.com/selvavp-hub/apex-lab) —
a daily series of real Salesforce & AI code projects demonstrating
Apex development, LWC, integrations, and applied AI.

---
*Generated as part of the daily Salesforce coding series.*
