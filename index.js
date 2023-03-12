// See https://github.com/dialogflow/dialogflow-fulfillment-nodejs
// for Dialogflow fulfillment library docs, samples, and to report issues
 
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion} = require('dialogflow-fulfillment');
const axios = require("axios");
const csv = require("fast-csv");
const _ = require("lodash");

process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
var database = [];

exports.dialogflowFirebaseFulfillment = functions.runWith({ timeoutSeconds: 60 }).https.onRequest( (request, response) => {

  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));
  console.log("Database rows: " + database.length);

  function getProductRecommendation(agent) {
    const type = agent.parameters.Type;
    const primaryColor = agent.parameters.color;
    const gender = agent.parameters.gender;
    const priceComparator = agent.parameters.PriceComparison;
    let price = agent.parameters.price;
    if (price)
      price = price.amount;
    
    console.log("Type: " + type);
    console.log("primaryColor: " + primaryColor);
    console.log("gender: " + gender);
    console.log("priceComparator: " + priceComparator);
    console.log("price: " + price);
    
    const productResults = _.filter(database, (obj) => {
      	let matches = false;      
      	if (_.isEmpty(type) === false) 
          matches = obj["Individual_category"].toLowerCase().trim() === type.toLowerCase().trim();      
      	//console.log("Matched category ?: " + matches.toString());
      	if (matches && _.isEmpty(gender) === false) 
          matches = matches && (obj["category_by_Gender"].toLowerCase().trim() === gender.toLowerCase().trim());
      	
      
        if (matches && _.isEmpty(priceComparator) === false) {
          	const itemPrice = obj["DiscountPrice (in Rs)"] !== "" ? Number.parseInt(obj["DiscountPrice (in Rs)"]) : 0;
            if (itemPrice !== 0) {
              const requestedPrice = price;
              //console.log(`ItemPrice: ${itemPrice}, requestedPrice: ${requestedPrice}`);
              const checkPrices = () => {
                if (priceComparator === "less") 
                  return itemPrice <= requestedPrice;
                else
                  return itemPrice >= requestedPrice;
              };
              matches = matches && checkPrices();
            }
          	else
              matches = false;
        }        
      	//console.log("Matched gender ?: " + matches.toString());
      
      	return matches;
    });

   

    if (productResults.length === 0) {
      agent.add(`I'm sorry, I couldn't find any products matching your description.`);
    } else {
      
      console.log("Matched Products: " + productResults.length.toString());
      const recommendedProduct = productResults[Math.floor(Math.random() * productResults.length)];
      console.log("Recommended Product: " + JSON.stringify(recommendedProduct));
     
    
      agent.add(`Check out this product: ${recommendedProduct["URL"]}`);
    }
    return agent;
  }
  
  let handlers = new Map();
  handlers.set("ProductRecommendation", getProductRecommendation);
  
  if (database.length === 0){
    axios.get("https://github.com/Aurovindhya/fashion-recommender-system/blob/csv/fashion-database.csv?raw=true").then(response => {
      csv.parseString(response.data, { headers: true })
          .on("data", (row) => database.push(row))
          .on("end", rowCount => {
              console.log("Database rows: " + rowCount.toString());
              console.log("Data[0]: " + JSON.stringify(database[0]));
              agent.handleRequest(handlers);
          });
    });
  }
  else {
    agent.handleRequest(handlers);
  }

});
