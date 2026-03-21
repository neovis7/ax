# SVG 차트 템플릿 라이브러리

visual-builder 에이전트가 참조하는 7종 SVG 차트 구현 패턴.
모든 차트는 design-tokens.css의 CSS 변수를 사용하며, 등장 애니메이션을 포함합니다.

## 목차

1. [도넛 차트 (Donut)](#1-도넛-차트-donut) — 비율(%) 표시
2. [비교 바 차트 (Comparison Bar)](#2-비교-바-차트-comparison-bar) — 항목 간 크기 비교
3. [레이더 차트 (Radar)](#3-레이더-차트-radar) — 다축 동시 비교
4. [와플 차트 (Waffle)](#4-와플-차트-waffle) — N 중 M 이산 비율
5. [게이지 차트 (Gauge)](#5-게이지-차트-gauge) — 단일 KPI
6. [트렌드라인 차트 (Trendline)](#6-트렌드라인-차트-trendline) — 시계열
7. [픽토그램 (Pictogram)](#7-픽토그램-pictogram) — 아이콘 비율
8. [공통 유틸리티](#공통-유틸리티) — CountUp, 색상 시퀀스, Tier 2 라이브러리

---

## 차트 선택 의사결정 트리

```
데이터 유형 확인:
│
├─ 비율(%) 데이터 → 도넛 차트
├─ A vs B 비교 (2~6 항목) → 비교 바 차트
├─ 다축(3+) 동시 비교 → 레이더 차트
├─ N명 중 M명 (이산 비율) → 와플/픽토그램
├─ 단일 KPI (목표 대비) → 게이지 차트
├─ 시계열 (트렌드) → 트렌드라인 차트
└─ 범주별 크기 비교 → 비교 바 차트
```

---

## 1. 도넛 차트 (Donut)

**용도**: 비율(%) 표시, 전체 대비 부분
**데이터**: `[{label, value, color}]`

```html
<div class="chart-donut" style="width:200px;height:200px;position:relative;">
  <svg viewBox="0 0 100 100" style="transform:rotate(-90deg);">
    <!-- 배경 트랙 -->
    <circle cx="50" cy="50" r="40" fill="none"
            stroke="var(--chart-grid)" stroke-width="12"/>
    <!-- 데이터 세그먼트 (stroke-dasharray로 비율 표현) -->
    <!-- 예: 65% = circumference(251.3) * 0.65 = 163.3 -->
    <circle cx="50" cy="50" r="40" fill="none"
            stroke="var(--chart-color-1)" stroke-width="12"
            stroke-dasharray="163.3 251.3"
            stroke-linecap="round"
            class="donut-segment">
      <animate attributeName="stroke-dasharray"
               from="0 251.3" to="163.3 251.3"
               dur="0.8s" fill="freeze"
               calcMode="spline" keySplines="0.4 0 0.2 1"/>
    </circle>
  </svg>
  <!-- 중앙 라벨 -->
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;
              align-items:center;justify-content:center;">
    <span style="font-family:var(--font-display);font-size:var(--font-size-4xl);
                 font-weight:var(--font-weight-bold);color:var(--chart-value);"
          class="count-up" data-target="65">0</span>
    <span style="font-size:var(--font-size-sm);color:var(--chart-label);">
      라벨 텍스트
    </span>
  </div>
</div>
```

**다중 세그먼트**: `stroke-dashoffset`으로 각 세그먼트의 시작점을 조절.

---

## 2. 비교 바 차트 (Comparison Bar)

**용도**: 항목 간 크기 비교
**데이터**: `[{label, value, maxValue}]`

```html
<div class="chart-bars" style="display:flex;flex-direction:column;gap:var(--space-4);">

  <!-- 항목 1 -->
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:var(--space-1);">
      <span style="font-size:var(--font-size-sm);color:var(--chart-label);">항목 A</span>
      <span style="font-size:var(--font-size-sm);font-weight:var(--font-weight-semibold);
                   color:var(--chart-value);">85%</span>
    </div>
    <div style="height:8px;background:var(--progress-track);border-radius:var(--radius-full);
                overflow:hidden;">
      <div style="height:100%;width:85%;background:var(--chart-color-1);
                  border-radius:var(--radius-full);
                  animation:bar-grow 0.6s var(--easing-out) forwards;"
           class="bar-fill"></div>
    </div>
  </div>

  <!-- 항목 2 -->
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:var(--space-1);">
      <span style="font-size:var(--font-size-sm);color:var(--chart-label);">항목 B</span>
      <span style="font-size:var(--font-size-sm);font-weight:var(--font-weight-semibold);
                   color:var(--chart-value);">62%</span>
    </div>
    <div style="height:8px;background:var(--progress-track);border-radius:var(--radius-full);
                overflow:hidden;">
      <div style="height:100%;width:62%;background:var(--chart-color-2);
                  border-radius:var(--radius-full);
                  animation:bar-grow 0.6s 0.1s var(--easing-out) both;"
           class="bar-fill"></div>
    </div>
  </div>

</div>

<style>
@keyframes bar-grow {
  from { width: 0%; }
}
</style>
```

---

## 3. 레이더 차트 (Radar)

**용도**: 3개 이상 축의 동시 비교
**데이터**: `[{axis, value}]` (value: 0~100)

```html
<svg viewBox="0 0 300 300" class="chart-radar" style="width:280px;height:280px;">
  <defs>
    <style>
      .radar-grid { stroke: var(--chart-grid); stroke-width: 0.5; fill: none; }
      .radar-axis { stroke: var(--chart-grid); stroke-width: 0.5; }
      .radar-area { fill: var(--chart-color-1); fill-opacity: 0.15;
                    stroke: var(--chart-color-1); stroke-width: 2; }
      .radar-dot  { fill: var(--chart-color-1); }
      .radar-label { font-family: var(--font-body); font-size: 11px;
                     fill: var(--chart-label); text-anchor: middle; }
    </style>
  </defs>

  <!-- 동심원 격자 (5단계) -->
  <circle cx="150" cy="150" r="120" class="radar-grid"/>
  <circle cx="150" cy="150" r="96"  class="radar-grid"/>
  <circle cx="150" cy="150" r="72"  class="radar-grid"/>
  <circle cx="150" cy="150" r="48"  class="radar-grid"/>
  <circle cx="150" cy="150" r="24"  class="radar-grid"/>

  <!-- 축선 (5축 예시, 72도 간격) -->
  <line x1="150" y1="150" x2="150" y2="30"  class="radar-axis"/>
  <line x1="150" y1="150" x2="264" y2="113" class="radar-axis"/>
  <line x1="150" y1="150" x2="220" y2="257" class="radar-axis"/>
  <line x1="150" y1="150" x2="80"  y2="257" class="radar-axis"/>
  <line x1="150" y1="150" x2="36"  y2="113" class="radar-axis"/>

  <!-- 데이터 영역 (다각형) -->
  <polygon points="150,42 252,113 207,245 93,245 48,113"
           class="radar-area">
    <animate attributeName="points"
             from="150,150 150,150 150,150 150,150 150,150"
             to="150,42 252,113 207,245 93,245 48,113"
             dur="0.6s" fill="freeze"
             calcMode="spline" keySplines="0.4 0 0.2 1"/>
  </polygon>

  <!-- 데이터 점 -->
  <circle cx="150" cy="42"  r="4" class="radar-dot"/>
  <circle cx="252" cy="113" r="4" class="radar-dot"/>
  <circle cx="207" cy="245" r="4" class="radar-dot"/>
  <circle cx="93"  cy="245" r="4" class="radar-dot"/>
  <circle cx="48"  cy="113" r="4" class="radar-dot"/>

  <!-- 축 라벨 -->
  <text x="150" y="20"  class="radar-label">축 1</text>
  <text x="275" y="113" class="radar-label">축 2</text>
  <text x="225" y="275" class="radar-label">축 3</text>
  <text x="75"  y="275" class="radar-label">축 4</text>
  <text x="25"  y="113" class="radar-label">축 5</text>
</svg>
```

**좌표 계산**: `x = cx + r * value/100 * sin(angle)`, `y = cy - r * value/100 * cos(angle)`

---

## 4. 와플 차트 (Waffle)

**용도**: N 중 M (이산 비율, 직관적 표현)
**데이터**: `{total, filled, label}`

```html
<div class="chart-waffle">
  <div style="display:grid;grid-template-columns:repeat(10,1fr);gap:3px;width:200px;">
    <!-- 100칸 중 채워진 칸 = filled, 빈 칸 = total - filled -->
    <!-- 예: 73/100 -->
    <div style="aspect-ratio:1;border-radius:var(--radius-sm);
                background:var(--chart-color-1);
                animation:waffle-pop 0.3s calc(var(--i,0) * 15ms) var(--easing-bounce) both;"
         class="waffle-cell filled"></div>
    <!-- ... 73개 filled ... -->
    <div style="aspect-ratio:1;border-radius:var(--radius-sm);
                background:var(--chart-grid);opacity:0.3;"
         class="waffle-cell empty"></div>
    <!-- ... 27개 empty ... -->
  </div>
  <div style="margin-top:var(--space-2);text-align:center;">
    <span style="font-family:var(--font-display);font-size:var(--font-size-3xl);
                 font-weight:var(--font-weight-bold);color:var(--chart-value);">
      73<span style="font-size:var(--font-size-lg);color:var(--chart-label);">/100</span>
    </span>
  </div>
</div>

<style>
@keyframes waffle-pop {
  from { transform: scale(0); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}
</style>
```

**구현 팁**: JavaScript 생성이 실용적. `for(i=0;i<100;i++)` 루프로 셀 생성, `i < filled`이면 filled 클래스.

---

## 5. 게이지 차트 (Gauge)

**용도**: 단일 KPI, 목표 대비 현재 값
**데이터**: `{value, max, label, unit}`

```html
<div class="chart-gauge" style="width:200px;position:relative;">
  <svg viewBox="0 0 200 120">
    <defs>
      <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%"   stop-color="var(--color-error)"/>
        <stop offset="50%"  stop-color="var(--color-warning)"/>
        <stop offset="100%" stop-color="var(--color-success)"/>
      </linearGradient>
    </defs>
    <!-- 반원 트랙 -->
    <path d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none" stroke="var(--chart-grid)" stroke-width="14"
          stroke-linecap="round"/>
    <!-- 값 아크 (78% 예시: 반원 길이 251.3 * 0.78 = 196) -->
    <path d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none" stroke="url(#gauge-gradient)" stroke-width="14"
          stroke-linecap="round"
          stroke-dasharray="196 251.3"
          class="gauge-arc">
      <animate attributeName="stroke-dasharray"
               from="0 251.3" to="196 251.3"
               dur="1s" fill="freeze"
               calcMode="spline" keySplines="0.4 0 0.2 1"/>
    </path>
  </svg>
  <div style="position:absolute;bottom:10px;left:50%;transform:translateX(-50%);
              text-align:center;">
    <span style="font-family:var(--font-display);font-size:var(--font-size-3xl);
                 font-weight:var(--font-weight-bold);color:var(--chart-value);"
          class="count-up" data-target="78">0</span>
    <span style="font-size:var(--font-size-sm);color:var(--chart-label);">%</span>
    <div style="font-size:var(--font-size-xs);color:var(--chart-label);margin-top:2px;">
      라벨 텍스트
    </div>
  </div>
</div>
```

---

## 6. 트렌드라인 차트 (Trendline)

**용도**: 시계열 추이, 성장/하락 시각화
**데이터**: `[{x, y}]`

```html
<svg viewBox="0 0 400 200" class="chart-trendline"
     style="width:100%;max-width:500px;height:auto;">
  <defs>
    <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="var(--chart-color-1)" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="var(--chart-color-1)" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- 그리드 라인 -->
  <line x1="40" y1="20"  x2="390" y2="20"  stroke="var(--chart-grid)" stroke-width="0.5" stroke-dasharray="4"/>
  <line x1="40" y1="60"  x2="390" y2="60"  stroke="var(--chart-grid)" stroke-width="0.5" stroke-dasharray="4"/>
  <line x1="40" y1="100" x2="390" y2="100" stroke="var(--chart-grid)" stroke-width="0.5" stroke-dasharray="4"/>
  <line x1="40" y1="140" x2="390" y2="140" stroke="var(--chart-grid)" stroke-width="0.5" stroke-dasharray="4"/>
  <line x1="40" y1="180" x2="390" y2="180" stroke="var(--chart-grid)" stroke-width="0.5"/>

  <!-- 영역 채우기 -->
  <path d="M40,160 L110,130 L180,140 L250,90 L320,70 L390,40 L390,180 L40,180 Z"
        fill="url(#trend-fill)"/>

  <!-- 트렌드 라인 -->
  <polyline points="40,160 110,130 180,140 250,90 320,70 390,40"
            fill="none" stroke="var(--chart-color-1)" stroke-width="2.5"
            stroke-linecap="round" stroke-linejoin="round"
            class="trend-line">
    <animate attributeName="stroke-dasharray"
             from="0 1000" to="1000 0"
             dur="1.2s" fill="freeze"
             calcMode="spline" keySplines="0.4 0 0.2 1"/>
  </polyline>

  <!-- 데이터 포인트 -->
  <circle cx="40"  cy="160" r="4" fill="var(--chart-color-1)" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.2s" begin="0.2s" fill="freeze"/>
  </circle>
  <circle cx="390" cy="40"  r="4" fill="var(--chart-color-1)" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.2s" begin="1.0s" fill="freeze"/>
  </circle>

  <!-- Y축 라벨 -->
  <text x="35" y="24"  text-anchor="end" style="font-size:10px;fill:var(--chart-label);">100</text>
  <text x="35" y="104" text-anchor="end" style="font-size:10px;fill:var(--chart-label);">50</text>
  <text x="35" y="184" text-anchor="end" style="font-size:10px;fill:var(--chart-label);">0</text>

  <!-- X축 라벨 -->
  <text x="40"  y="196" text-anchor="middle" style="font-size:10px;fill:var(--chart-label);">1월</text>
  <text x="390" y="196" text-anchor="middle" style="font-size:10px;fill:var(--chart-label);">6월</text>
</svg>
```

---

## 7. 픽토그램 (Pictogram)

**용도**: 인원/개수의 직관적 비율 표현 (와플의 아이콘 버전)
**데이터**: `{total, highlighted, icon}`

```html
<div class="chart-pictogram" style="display:flex;flex-wrap:wrap;gap:var(--space-2);
            max-width:240px;">
  <!-- 10명 중 7명 강조 예시 -->
  <!-- 강조된 아이콘 (1~7) -->
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
       stroke="var(--chart-color-1)" stroke-width="1.5" stroke-linecap="round"
       style="animation:picto-pop 0.3s calc(0 * 60ms) var(--easing-bounce) both;">
    <circle cx="12" cy="8" r="4"/>
    <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
  </svg>
  <!-- ... 7개 강조 ... -->

  <!-- 비강조 아이콘 (8~10) -->
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
       stroke="var(--chart-grid)" stroke-width="1.5" stroke-linecap="round"
       style="opacity:0.3;">
    <circle cx="12" cy="8" r="4"/>
    <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
  </svg>
  <!-- ... 3개 비강조 ... -->
</div>

<style>
@keyframes picto-pop {
  from { transform: scale(0) rotate(-10deg); opacity: 0; }
  to   { transform: scale(1) rotate(0deg);   opacity: 1; }
}
</style>
```

**아이콘 변형**: 사람(기본), 체크마크, 별, 하트 등 도메인에 맞게 교체.

---

## 공통 유틸리티

### CountUp 애니메이션 (숫자 카운트)

```html
<script>
document.querySelectorAll('.count-up').forEach(el => {
  const target = parseInt(el.dataset.target);
  const duration = 1200;
  const start = performance.now();
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
    el.textContent = Math.round(target * eased);
    if (progress < 1) requestAnimationFrame(step);
  };
  // IntersectionObserver로 뷰포트 진입 시 시작
  new IntersectionObserver(([e]) => {
    if (e.isIntersecting) { requestAnimationFrame(step); }
  }, {threshold: 0.5}).observe(el);
});
</script>
```

### 차트 색상 시퀀스

차트에 여러 데이터 시리즈가 있을 때 순서대로 사용:
```css
--chart-color-1  /* 주 데이터 */
--chart-color-2  /* 보조 데이터 */
--chart-color-3  /* 3번째 */
--chart-color-4  /* 4번째 */
--chart-color-5  /* 5번째 (회색 계열, 기타용) */
```

### Tier 2 라이브러리 조건부 로드

차트 5개 이상 또는 인터랙티브 필요 시:
```html
<!-- Chart.js CDN (조건부) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>

<!-- ECharts CDN (조건부) -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

SVG 커스텀 차트가 기본. 라이브러리는 복잡한 인터랙션이 필요할 때만 사용.
