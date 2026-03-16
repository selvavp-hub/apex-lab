@IsTest
private class LeadEnrichmentQueueable_Test {

    @TestSetup
    static void makeData() {
        insert new Lead(
            LastName = 'Doe',
            Company  = 'Unknown Co',
            Email    = 'john.doe@example.com'
        );
    }

    @IsTest
    static void testQueueableEnqueues() {
        Lead lead = [SELECT Id FROM Lead LIMIT 1];

        // Register mock callout response
        Test.setMock(HttpCalloutMock.class, new EnrichmentMock());

        Test.startTest();
        Id jobId = LeadEnrichmentQueueable.enrich(new List<Id>{ lead.Id });
        Test.stopTest();

        Assert.isNotNull(jobId);
    }

    // ─── Mock HTTP Callout ────────────────────────────────────────────────────

    private class EnrichmentMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setBody('{"companyName":"Acme","industry":"Technology","employeeCount":500}');
            return res;
        }
    }
}
