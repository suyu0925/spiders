// Learn more about F# at http://docs.microsoft.com/dotnet/fsharp

open System

[<EntryPoint>]
let main argv =
    HaveFun.CnblogSpider.Run() |> Async.RunSynchronously

    0 // return an integer exit code
