// ============================================================
// 实验 E: framefit 实际可用性验证（修正 API）
// fit-copy 签名: fit-copy(min: 70%, max: none, max-lines, steps: 24,
//                        only-if-overflow: false, body)
// 无 width/height 参数 —— 用 layout(size => ...) 回调的内容可用尺寸
// ============================================================
#import "@preview/framefit:0.1.0": fit-copy

#set page(width: 300pt, height: 400pt, margin: 15pt)

// 固定版心 block 约束尺寸, fit-copy 用 layout 回调的 size 作 frame
#block(width: 250pt, height: 330pt, clip: true, breakable: false, stroke: 0.5pt + gray)[
  #fit-copy(
    min: 50%,
    max: 100%,
    steps: 24,
    only-if-overflow: true,
    [
      这是一段用于触发 framefit 自动缩放的正文。The quick brown fox jumps over the lazy dog.
      再多写一些内容确保溢出。内容继续延伸, 直到超过固定版心高度, 触发 framefit 的二分缩放。
      继续填充, 继续填充, 继续填充, 让这段文本足够长, 以验证 framefit 的收敛行为。
      The quick brown fox jumps over the lazy dog. More content here to make it overflow.
      这是用于验证 autofit 的关键实验。内容必须足够多, 才能触发字号缩放。
      当内容超过版心高度时, framefit 应二分缩小字号, 使内容恰好放下。
      继续, 继续, 继续, 继续, 继续, 确保内容确实超过版心高度。]
  )
]

#v(6pt)
#text(size: 8pt, fill: gray)[实验 E: framefit fit-copy 基本用法 (min:50% max:100% only-if-overflow)]
