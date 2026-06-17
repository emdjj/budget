// ============================================================
// 学习通作业 → 刷题 App JSON 提取脚本
// 使用方法：打开已批改的作业页面 → F12 → 控制台 → 粘贴回车
// ============================================================
(async function() {
  console.log('%c📖 学习通刷题提取器 v1.0', 'font-size:18px;font-weight:bold;color:#4fc3f7');

  // ========== 1. 查找题目容器 ==========
  const strategies = [
    // 策略A: TiMu (最常见)
    { container: '.TiMu', typeEl: '.clearfix', optionEl: '.answerBg .answerItem, .answerBg li, .answerBg p', correctCls: '.dui, .correct, .rightAnswer' },
    // 策略B: questionLi (新版)
    { container: '.questionLi', typeEl: '.questionType, .typeFlag', optionEl: '.options label, .optionItem, .chooseOption', correctCls: '.correct, .dui, .right' },
    // 策略C: ZyQuestion
    { container: '.ZyQuestion', typeEl: '.ZyQuestionType, .type', optionEl: '.ZyQuestionOption, .option', correctCls: '.ZyCorrect, .dui, .correct' },
    // 策略D: examQuestion
    { container: '.examQuestion', typeEl: '.questionType, .typeTitle', optionEl: '.option, .itemLabel', correctCls: '.correct, .dui' },
    // 策略E: 通用 - 按题型文字分组
    { container: '.topic-item, .question-item, .q-item', typeEl: '.q-type, .type-tag', optionEl: '.q-option, .opt-item', correctCls: '.correct, .dui' },
  ];

  let questions = [];
  let usedStrategy = null;

  for (const strat of strategies) {
    const containers = document.querySelectorAll(strat.container);
    if (containers.length === 0) continue;

    console.log(`🔍 尝试策略: ${strat.container} (找到 ${containers.length} 个容器)`);

    for (let i = 0; i < containers.length; i++) {
      const c = containers[i];
      const html = c.innerHTML;
      const text = c.textContent.trim();

      // ------ 提取题型 ------
      let type = 'single';
      if (/多选题|multiple/i.test(text)) type = 'multiple';
      else if (/判断题|truefalse|T.*F/i.test(text)) type = 'truefalse';
      else if (/单选题|single/i.test(text)) type = 'single';
      // 也检查 typeEl
      if (strat.typeEl) {
        const typeE = c.querySelector(strat.typeEl);
        if (typeE) {
          const t = typeE.textContent;
          if (/多选题/.test(t)) type = 'multiple';
          else if (/判断题/.test(t)) type = 'truefalse';
        }
      }

      // ------ 提取题目文本 ------
      let question = '';
      // 尝试从 typeEl 提取（通常 type+题目在一起）
      if (strat.typeEl) {
        const qEl = c.querySelector(strat.typeEl);
        if (qEl) {
          question = qEl.textContent
            .replace(/[【】\[\]（）()\s]*(单选题|多选题|判断题|single|multiple|truefalse)\s*/gi, '')
            .replace(/^[\s\.、\d]+/, '')  // 去掉序号 "1." "1、" 等
            .trim();
        }
      }
      // 如果题目太短，尝试从更大的范围提取
      if (!question || question.length < 3) {
        // 提取容器中第一个有意义的文本块
        const firstText = c.children[0]?.textContent?.trim() || '';
        question = firstText
          .replace(/[【】\[\]（）()\s]*(单选题|多选题|判断题|single|multiple|truefalse)\s*/gi, '')
          .replace(/^[\s\.、\d]+/, '')
          .trim();
      }
      if (!question || question.length < 3) question = text.slice(0, 80);

      // ------ 提取选项 ------
      const options = [];
      let optionElements = [];
      if (strat.optionEl) {
        optionElements = c.querySelectorAll(strat.optionEl);
      }
      // 如果没找到，尝试找所有常见的选项元素
      if (optionElements.length === 0) {
        optionElements = c.querySelectorAll('.answerItem, .answerBg li, .answerBg p, .optionItem, .chooseOption, label, .ZyQuestionOption, .option, .itemLabel, .q-option, .opt-item');
      }

      // 过滤：只取看起来像选项的（含 A. B. C. D. 或 A、B、 或 正确/错误）
      const seen = new Set();
      for (const opt of optionElements) {
        const t = opt.textContent.trim();
        if (!t || t.length < 1) continue;
        // 去重
        const key = t.replace(/[✓✔✗✘\s]/g, '');
        if (seen.has(key)) continue;
        seen.add(key);
        // 判断是否像选项
        if (/^[A-Da-d][.、\s]/.test(t) || /^[A-Da-d]\)/.test(t) || t.length > 1) {
          // 去掉前缀字母和符号
          const clean = t.replace(/^[A-Da-d][.、\)]\s*/, '').replace(/[✓✔✗✘]$/, '').trim();
          if (clean && !options.includes(clean)) options.push(clean);
        }
      }

      // 如果是判断题，强制设选项
      if (type === 'truefalse' && (options.length === 0 || options.length > 2)) {
        options.length = 0;
        options.push('正确', '错误');
      }

      // ------ 提取正确答案 ------
      let answer = type === 'multiple' ? [] : '';

      // 方法1: 找正确答案面板
      const answerPanel = c.querySelector('.answer_panel, .correctAnswer, .answer, .rightAnswerPanel, .correct-panel');
      if (answerPanel) {
        const ansText = answerPanel.textContent;
        if (type === 'multiple') {
          const matches = ansText.match(/[A-D]/g);
          if (matches) answer = matches.map(m => String(m.charCodeAt(0) - 65));
        } else if (type === 'truefalse') {
          answer = /正确|对|√|T/i.test(ansText) ? '0' : '1';
        } else {
          const m = ansText.match(/[A-D]/);
          if (m) answer = String(m[0].charCodeAt(0) - 65);
        }
      }

      // 方法2: 找 marked 正确的选项（有 dui / correct 类）
      if (!answer || (type !== 'multiple' && answer === '') || (type === 'multiple' && answer.length === 0)) {
        const correctOptions = c.querySelectorAll(strat.correctCls);
        if (correctOptions.length > 0) {
          if (type === 'multiple') {
            answer = [];
            correctOptions.forEach(el => {
              const parentText = el.closest(strat.optionEl)?.textContent || el.textContent;
              const m = parentText.match(/([A-D])/);
              if (m) answer.push(String(m[1].charCodeAt(0) - 65));
            });
          } else if (type === 'truefalse') {
            const firstCorrect = correctOptions[0].textContent;
            answer = /正确|对|√|T/i.test(firstCorrect) ? '0' : '1';
          } else {
            const firstCorrect = correctOptions[0].closest(strat.optionEl)?.textContent || correctOptions[0].textContent;
            const m = firstCorrect.match(/([A-D])/);
            if (m) answer = String(m[1].charCodeAt(0) - 65);
          }
        }
      }

      // 方法3: 找 ✓ check 标记
      if (!answer || (type !== 'multiple' && answer === '') || (type === 'multiple' && answer.length === 0)) {
        optionElements.forEach((opt, idx) => {
          if (/[✓✔✅]/.test(opt.textContent)) {
            if (type === 'multiple') {
              if (!Array.isArray(answer)) answer = [];
              answer.push(String(idx));
            } else {
              answer = String(idx);
            }
          }
        });
      }

      questions.push({ type, question, options, answer, explanation: '' });
    }

    if (questions.length > 0) {
      usedStrategy = strat.container;
      break;
    }
  }

  // ========== 2. 如果上面的策略都没找到 ==========
  if (questions.length === 0) {
    console.log('%c❌ 自动识别失败，正在生成备用方案...', 'color:#ef5350;font-size:14px');
    console.log('%c📋 请复制以下信息告诉我，我来帮你改进脚本:', 'color:#ffa726');
    console.log('页面标题:', document.title);
    console.log('页面 URL:', location.href);
    // 输出页面结构快照
    const bodyHTML = document.body.innerHTML.slice(0, 5000);
    console.log('页面结构样本:', bodyHTML);
    return;
  }

  // ========== 3. 去空 & 清理 ==========
  questions = questions.filter(q => q.question && q.question.length > 2 && q.options.length >= 2);

  // ========== 4. 输出结果 ==========
  console.log(`%c✅ 成功提取 ${questions.length} 题！`, 'color:#66bb6a;font-size:16px;font-weight:bold');

  // 按题型统计
  const stats = {};
  questions.forEach(q => { stats[q.type] = (stats[q.type] || 0) + 1; });
  console.log('📊 统计:', Object.entries(stats).map(([k,v]) => {
    const labels = { single: '单选题', multiple: '多选题', truefalse: '判断题' };
    return `${labels[k]||k}: ${v}题`;
  }).join(' | '));
  console.log('');

  // 输出 JSON
  const json = JSON.stringify(questions, null, 2);
  console.log('%c📋 复制下面的 JSON 导入刷题 App：', 'font-size:14px;font-weight:bold');
  console.log('%c' + '-'.repeat(50), 'color:#4fc3f7');
  console.log(json);
  console.log('%c' + '-'.repeat(50), 'color:#4fc3f7');

  // 自动复制到剪贴板
  try {
    await navigator.clipboard.writeText(json);
    console.log('%c📋 已自动复制到剪贴板！去刷题 App 粘贴导入即可。', 'color:#66bb6a;font-size:14px');
  } catch(e) {
    console.log('%c⚠️ 自动复制失败，请手动复制上面的 JSON', 'color:#ffa726');
  }

  // 输出简要预览
  console.log('\n📝 预览：');
  questions.slice(0, 3).forEach((q, i) => {
    const labels = { single: '单选', multiple: '多选', truefalse: '判断' };
    console.log(`  ${i+1}. [${labels[q.type]||q.type}] ${q.question.slice(0, 40)}`);
    q.options.forEach((o, j) => console.log(`     ${'ABCDEFGH'[j]||j}. ${o}`));
    const ansStr = Array.isArray(q.answer) ? q.answer.map(a => 'ABCDEFGH'[parseInt(a)]||a).join(',') : ('ABCDEFGH'[parseInt(q.answer)] || q.answer);
    console.log(`     ✅ 答案: ${ansStr}`);
  });
  if (questions.length > 3) console.log(`  ... 还有 ${questions.length - 3} 题`);
})();
