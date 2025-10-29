import { HelpCircle } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqData = [
  {
    question: "How does AI-powered product recommendation work?",
    answer: "sandh.ai uses advanced machine learning algorithms that analyze your browsing behavior, preferences, and purchase history to suggest products tailored specifically for you. Our hybrid recommendation system combines collaborative filtering with content-based analysis to ensure highly accurate suggestions.",
  },
  {
    question: "Are the recommendations personalized for each user?",
    answer: "Yes! Every recommendation is uniquely generated based on your individual profile, past interactions, and preferences. The more you use sandh.ai, the better our AI understands your needs and provides increasingly accurate product suggestions.",
  },
  {
    question: "How can I chat with the AI assistant?",
    answer: "Simply click the floating chat button in the bottom-right corner of the page. Our AI assistant can help you find products, answer questions about specifications, compare items, and provide personalized shopping advice 24/7.",
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit and debit cards, UPI payments, net banking, and popular digital wallets. All transactions are secured with industry-standard encryption to protect your financial information.",
  },
  {
    question: "What is your return and refund policy?",
    answer: "We offer a hassle-free 30-day return policy on most products. If you're not satisfied with your purchase, you can initiate a return through your account dashboard. Refunds are processed within 5-7 business days after we receive the returned item.",
  },
  {
    question: "How do I track my order?",
    answer: "Once your order is shipped, you'll receive a tracking number via email and SMS. You can also track your order in real-time through your account dashboard under 'My Orders'. Our system provides live updates on your package's location and estimated delivery time.",
  },
];

export const FAQ = () => {
  return (
    <section className="py-12" id="faq">
      <div className="mb-8 flex items-center gap-3">
        <div className="p-2 bg-accent/10 rounded-lg">
          <HelpCircle className="h-6 w-6 text-accent" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-foreground">Frequently Asked Questions</h2>
          <p className="text-muted-foreground">Everything you need to know about sandh.ai</p>
        </div>
      </div>

      <div className="w-full">
        <Accordion type="single" collapsible className="w-full">
          {faqData.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left text-foreground hover:text-primary">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
};
