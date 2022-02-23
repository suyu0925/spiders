namespace HaveFun

open System
open System.Threading
open System.Threading.Tasks
open System.Collections.Generic
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
open DotnetSpider.Proxy

type Parser() =
    inherit DataParser()

    override this.InitializeAsync() : Task =
        this.AddRequiredValidator("cnblogs\\.com")
        // this.AddFollowRequestQuerier(Selectors.XPath("."))
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
        let properties =
            Dictionary<string, obj>(
                dict [
                    "Timeout", 10000 :> obj
                    "网站", "博客园" :> obj
                ]
            )

        this.AddRequestsAsync(new Request("http://www.cnblogs.com/", properties))
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

type ClashProxySuplier() =
    interface IProxySupplier with
        member this.GetProxiesAsync() : Task<IEnumerable<Uri>> =
            Task.FromResult(seq [ Uri("http://localhost:7890") ])

module CnblogSpider =
    let Run () =
        let builder = Builder.CreateDefaultBuilder<CnblogSpider>(fun x -> x.Speed <- 5.0)

        builder
            // .UseSerilog()
            .UseDownloader<HttpClientDownloader>()
            .UseQueueDistinctBfsScheduler<HashSetDuplicateRemover>()
            .UseProxy<ClashProxySuplier, DefaultProxyValidator>(fun _ -> ())
            .IgnoreServerCertificateError()
            .Build()
            .RunAsync()
        |> Async.AwaitTask
