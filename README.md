# mt5-rest-python

Open / close a trade using the MT5 API with Python and API REST, so it can receving signal from another software like TradingView with webhook.

## What this software do

Expose API REST `/signal` where we can alert our program to open a trade.

You can modify the request to pass more parameters like volume, stop loss and many many more.

## Example of usage

Request

```sh
$ curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"pair":"EURUSD","action":"BUY"}' \
  http://localhost:5000/signal
```

Response
```
200 OK { "success": "Order successfully opened! " }
```
