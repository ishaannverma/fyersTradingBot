# fyersTradingBot

## Login
Click on the login link and paste the link you are directed to back into the console. <br>
_Note: This can be avoided if there is a token less than 14 hours old. In that case, the software will auto-login._

## Telegram
The app will send Telegram messages of updates to the specified telegram account. The app can also be controlled by the said account through chat.

## Symbol Class
Represents a single symbol that tracks the `Symbol.ticker`, `Symbol.ltp`, and `Symbol.time`.<br>
Also used for getting option contracts for that symbol.

## Symbols Class
The class returns a `symbolsHandler` that will hold all the symbols that are used in the app.
`get(symbol)` method will return a `singleSymbol` object for the given symbol.

