// props: any 導致沒有任何型別保護，無法在編譯期發現錯誤
const TodoItem = (props: any) => {
  // 巢狀三元：計算了 statusLabel 但從未在 return 中使用（dead code）
  const statusLabel = props.completed
    ? '已完成'
    : props.priority === 'high'
    ? '緊急'
    : '進行中';

  return (
    <div className="todo-item">
      <span style={{ textDecoration: props.completed ? 'line-through' : 'none' }}>
        {props.title}
      </span>
      {/* 巢狀三元運算子，應改用 statusLabel 或 if/else */}
      <span>
        {props.completed ? '已完成' : props.priority === 'high' ? '緊急' : '進行中'}
      </span>
    </div>
  );
};

export default TodoItem;
