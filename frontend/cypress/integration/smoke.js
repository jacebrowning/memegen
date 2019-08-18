describe("My First Test", function() {
  it('finds the content "type"', function() {
    var site = Cypress.env("SITE");

    console.log(site);
    cy.visit(site);

    cy.get("img");

    cy.contains("API").click();
  });
});
