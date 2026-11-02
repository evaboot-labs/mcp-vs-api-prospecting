# When to use the MCP, when to use the API

## What we measured (2026-11-02)

One Sales Navigator lead list of 9 sales leaders, exported through both paths on the same Evaboot account.

| | Evaboot MCP (in Claude) | Evaboot API (Python) |
|---|---|---|
| Leads returned | 9 | 9 |
| Safe emails | 9 | 9 |
| Columns per lead | 67 | 67 |
| Calls | 5 tool calls | 4 HTTP calls |
| Time to rows | 26 s | 12 s |
| Credits | 9 | 9 |
| Code written | none | 76 lines |

Every email and email status matched. The data is the same: only the path changes.

## What differs

- **Cap.** The MCP export tool takes `max_results`. The API exports every lead in the search or list, at 1 credit per lead.
- **Search building.** The API search builder answered in 3.3 s with literal filters. The MCP search agent took a few minutes, went company-first, widened the region and added local-language titles.
- **Data in the chat.** 9 leads were about 50 KB of text. Through the MCP, all of it goes into the agent's context: for big exports, push them to a CRM or a sheet instead.
- **Repeat runs.** A script runs the same way every time. An agent can change its arguments or stop to ask a question.
- **Errors.** With the API, your code handles 202 (poll again), 402 (credits), 409 (no usable Sales Navigator seat), 429 (quota or rate limit). LinkedIn rate limits on the seat hit both paths.

## The rule

| Use the MCP when | Use the API when |
|---|---|
| A rep or manager does the work | The export runs on a schedule, unattended |
| The request changes every time | The leads feed another system |
| You want the agent to build the search | You need predictable runs and logs |
| The export is small, or goes to a CRM | Someone writes and maintains the code |

Most teams use both: reps explore through the MCP, and the searches that work become scheduled API jobs or Evaboot recurring exports.

Back to the [README](../README.md).
