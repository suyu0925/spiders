module HaveFun

open System.Threading
open System.Threading.Tasks
open Microsoft.Extensions.Hosting
open Microsoft.Extensions.Options
open Microsoft.Extensions.Logging
open DotnetSpider
open DotnetSpider.DataFlow
open DotnetSpider.DataFlow.Parser
open DotnetSpider.Downloader
open DotnetSpider.Http
open DotnetSpider.Selector
open DotnetSpider.Infrastructure
open DotnetSpider.Scheduler
open DotnetSpider.Scheduler.Component
open Serilog

type Parser() =
    inherit DataParser()

    override this.InitializeAsync() : Task =
        this.AddRequiredValidator("cnblogs\\.com")
        this.AddFollowRequestQuerier(Selectors.XPath("."))
        Task.CompletedTask

    override this.ParseAsync(context: DataFlowContext) : Task =
        context.AddData("URL", context.Request.RequestUri)
        let s = context.Selectable.XPath(".//title")

        if not (s |> isNull) then
            context.AddData("Title", s.Value)

        Task.CompletedTask

type CnblogSpider(options: IOptions<SpiderOptions>, services: DependenceServices, logger: ILogger<Spider>) =
    inherit Spider(options, services, logger)

    member this.addDataFlow() =
        this.AddDataFlow(new Parser()) |> ignore
        this.AddDataFlow(new ConsoleStorage()) |> ignore

    member this.addRequest() =
        this.AddRequestsAsync(new Request("http://www.cnblogs.com/"))
        |> Async.AwaitTask

    override this.InitializeAsync(stoppingToken) : Task =
        async {
            let! request = this.addRequest ()
            this.addDataFlow ()
        }
        |> Async.StartAsTask
        :> Task

    override this.GenerateSpiderId() : SpiderId =
        SpiderId(ObjectId.CreateId().ToString(), "博客园")

let RunCnblogSpider () =
    Builder
        .CreateDefaultBuilder<CnblogSpider>(fun x -> x.Speed <- 5.0)
        // .UseSerilog()
        .UseDownloader<HttpClientDownloader>()
        .UseQueueDistinctBfsScheduler<HashSetDuplicateRemover>()
        .Build()
        .RunAsync()
    |> Async.AwaitTask
