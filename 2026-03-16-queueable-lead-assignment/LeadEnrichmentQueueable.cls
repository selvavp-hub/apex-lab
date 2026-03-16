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

    // ─── Private helpers ──────────────────────────────────────────────────────

    private EnrichmentResult callEnrichmentAPI(String email) {
        if (String.isBlank(email)) return null;

        HttpRequest req = new HttpRequest();
        req.setEndpoint(API_ENDPOINT + '?email=' + EncodingUtil.urlEncode(email, 'UTF-8'));
        req.setMethod('GET');
        req.setHeader('Accept', 'application/json');
        req.setTimeout(10000);

        HttpResponse res = new Http().send(req);

        if (res.getStatusCode() == 200) {
            return (EnrichmentResult) JSON.deserialize(
                res.getBody(), EnrichmentResult.class
            );
        }
        System.debug('Enrichment API error: ' + res.getStatusCode());
        return null;
    }

    // ─── Inner class for API response ─────────────────────────────────────────

    public class EnrichmentResult {
        public String  companyName;
        public String  industry;
        public Integer employeeCount;
        public String  website;
    }

    // ─── Static launcher ──────────────────────────────────────────────────────

    public static Id enrich(List<Id> leadIds) {
        return System.enqueueJob(new LeadEnrichmentQueueable(leadIds));
    }
}
