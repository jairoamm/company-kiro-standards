@HU-DEMO-001
Feature: Consulta de pedido con datos sintéticos

  Background:
    * def configuredBaseUrl = karate.properties['baseUrl'] || java.lang.System.getenv('BASE_URL')
    * if (!configuredBaseUrl) karate.fail('BASE_URL debe identificar el destino autorizado')
    * url configuredBaseUrl
    * def data = read('test-data.json')

  @CP-007
  Scenario: consultar un pedido existente
    Given path 'orders', data.existingOrderId
    When method get
    Then status 200
    And match response contains { id: '#string', status: '#string' }
    And match response.id == data.existingOrderId

  @CP-008
  Scenario: rechazar un identificador con formato inválido
    Given path 'orders', data.invalidOrderId
    When method get
    Then status 400
    And match response.code == 'INVALID_ORDER_ID'
