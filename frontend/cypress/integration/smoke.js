describe("My First Test", function() {
  it('finds the content "type"', function() {
    var site = Cypress.env("SITE") || "http://localhost:5000";

    cy.visit(site);

    cy.get("img");

    cy.contains("API").click();
  });
});
