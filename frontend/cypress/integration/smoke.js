var site = Cypress.env("SITE") || "http://localhost:5000";

describe("Default Content", function() {
  it("contains an image preview", function() {
    cy.visit(site);

    cy.get("img").should("be.visible");
  });
});

describe("Developer Links", function() {
  it("opens the API", function() {
    cy.visit(site);

    cy.contains("API").click();

    cy.contains("templates");
    cy.contains("images");
  });

  it("opens the API documentation", function() {
    cy.visit(site);

    cy.contains("Documentation").click();

    cy.contains("Swagger UI");
  });
});
