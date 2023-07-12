import { FC } from 'react';
import { Box } from '../Layout/Box';
import { Icon, IconType, IconValue } from '../Layout/Icon';

interface ChatKickoffProps {
  onExampleClick: (prompt: string) => void;
}

interface ChatKickoffBox {
  icon: {
    value: IconValue;
    type?: IconType;
  };
  title: string;
  body: JSX.Element;
}

export const ChatKickoff: FC<ChatKickoffProps> = ({ onExampleClick }) => {
  const examplesPrompts = [
    'Home prices in Los Angeles',
    'What was the most expensive ZIP in CA in January 2023?',
    'Total homes sold in Los Angeles in 2023 broken down by building type',
  ];
  const handleExampleClick = (prompt: string) => {
    return () => onExampleClick(prompt);
  };
  const BOXES: ChatKickoffBox[] = [
    {
      icon: { value: 'bolt' },
      title: 'Capabilities',
      body: (
        <>
          <h3>
            This is a first release, with limited functionality. It enables{' '}
            <b>only</b> the following:
          </h3>
          <ul className="list list-decimal">
            {[
              <>
                Generate only 1 paragraph summary about a real estate topic. The
                data available includes only: rents, sales prices, listing
                prices, price per square foot, # of homes sold, inventory and
                number of pending sales.{' '}
                <b>No other data included in this release</b>.
              </>,
              <>Generate 1 data viz</>,
            ].map((listItem, idx) => (
              <li className="ml-4" key={idx}>
                {listItem}
              </li>
            ))}
          </ul>
        </>
      ),
    },
    {
      icon: { value: 'lightbulb' },
      title: 'Examples',
      body: (
        <ul className="flex flex-col gap-2 w-full">
          {examplesPrompts.map((prompt, idx) => (
            <li key={idx}>
              <button
                className="w-full bg-transparent border-none text-start text-blue-600 cursor-pointer hover:text-blue-800 focus:outline-none focus:ring-0 flex items-center justify-between gap-2"
                onClick={handleExampleClick(prompt)}
              >
                <span>{prompt}</span>
                <Icon value="arrow_circle_right" type="filled"></Icon>
              </button>
            </li>
          ))}
        </ul>
      ),
    },
    {
      icon: { value: 'warning_amber', type: 'round' },
      title: 'Limitations',
      body: (
        <>
          <h3>
            With this early release, please note the following limitations:
          </h3>
          <ul className="list list-disc">
            {[
              'Data timeframe: Only January 1 2020 onward is supported',
              'Geographies: Only United States states, counties, cities, and zip codes. All other geographies, for example neighborhoods, are NOT supported.',
            ].map((listItem, idx) => (
              <li className="ml-4" key={idx}>
                {listItem}
              </li>
            ))}
          </ul>
        </>
      ),
    },
  ];
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-8">
      {BOXES.map(
        ({ title, body, icon: { value: iconValue, type: iconType } }, idx) => (
          <Box key={idx}>
            <div className="flex flex-col items-start space-y-2 text-secondary-dark">
              <Icon
                className="text-5xl self-center"
                value={iconValue}
                type={iconType}
              ></Icon>
              <h2 className="self-center text-xl font-semibold">{title}</h2>
              {body}
            </div>
          </Box>
        ),
      )}
    </div>
  );
};
