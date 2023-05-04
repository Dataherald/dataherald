import React, {
  CSSProperties,
  ReactNode,
  cloneElement,
  isValidElement,
  memo,
} from "react";

interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className,
  style,
}) => {
  const childButtons = React.Children.map(
    children,
    (child: React.ReactNode, index: number) => {
      if (!isValidElement(child)) {
        return child;
      }

      const isFirst = index === 0;
      const isLast = index === React.Children.count(children) - 1;

      let borderRadius = "rounded-none";

      if (isFirst) {
        borderRadius += " rounded-l-lg";
      } else if (isLast) {
        borderRadius += " rounded-r-lg";
      }

      const updatedClassName = `${child.props.className || ""} ${borderRadius}`;
      const updatedProps = Object.assign({}, child.props, {
        className: updatedClassName,
      });
      return cloneElement(child, updatedProps);
    }
  );

  return (
    <div className={`${className} flex`} style={style}>
      {childButtons}
    </div>
  );
};

export default memo(ButtonGroup);
