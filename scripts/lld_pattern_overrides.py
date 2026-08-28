"""Canonical C++17 examples for the LLD design-pattern chapters."""

from __future__ import annotations

from textwrap import dedent


def cpp(source: str) -> str:
    return dedent(source).strip()


PATTERN_SNIPPETS = {
    "lld-1creational-design-pattern-1-singleton": cpp(
        r"""
        #include <iostream>

        class Singleton {
        public:
            static Singleton& instance() {
                // A function-local static is initialized once in a thread-safe way since C++11.
                static Singleton value;
                return value;
            }

            Singleton(const Singleton&) = delete;
            Singleton& operator=(const Singleton&) = delete;

            void log(const char* message) const {
                std::cout << message << '\n';
            }

        private:
            Singleton() = default;
        };

        int main() {
            Singleton::instance().log("one shared instance");
            std::cout << std::boolalpha
                      << (&Singleton::instance() == &Singleton::instance()) << '\n';
        }
        """
    ),
    "lld-1creational-design-pattern-2-factory-method": cpp(
        r"""
        #include <iostream>
        #include <memory>

        class Document {
        public:
            virtual ~Document() = default;
            virtual void open() const = 0;
        };

        class TextDocument final : public Document {
        public:
            void open() const override { std::cout << "Opening text document\n"; }
        };

        class Spreadsheet final : public Document {
        public:
            void open() const override { std::cout << "Opening spreadsheet\n"; }
        };

        class Application {
        public:
            virtual ~Application() = default;
            void newDocument() const {
                auto document = createDocument();
                document->open();
            }

        protected:
            // Subclasses decide which concrete product the factory method creates.
            virtual std::unique_ptr<Document> createDocument() const = 0;
        };

        class TextApplication final : public Application {
        protected:
            std::unique_ptr<Document> createDocument() const override {
                return std::make_unique<TextDocument>();
            }
        };

        class SheetApplication final : public Application {
        protected:
            std::unique_ptr<Document> createDocument() const override {
                return std::make_unique<Spreadsheet>();
            }
        };

        int main() {
            TextApplication textApp;
            SheetApplication sheetApp;
            textApp.newDocument();
            sheetApp.newDocument();
        }
        """
    ),
    "lld-1creational-design-pattern-3-abstract-factory": cpp(
        r"""
        #include <iostream>
        #include <memory>

        class Button {
        public:
            virtual ~Button() = default;
            virtual void paint() const = 0;
        };

        class Checkbox {
        public:
            virtual ~Checkbox() = default;
            virtual void paint() const = 0;
        };

        class WindowsButton final : public Button {
        public:
            void paint() const override { std::cout << "Windows button\n"; }
        };

        class WindowsCheckbox final : public Checkbox {
        public:
            void paint() const override { std::cout << "Windows checkbox\n"; }
        };

        class MacButton final : public Button {
        public:
            void paint() const override { std::cout << "macOS button\n"; }
        };

        class MacCheckbox final : public Checkbox {
        public:
            void paint() const override { std::cout << "macOS checkbox\n"; }
        };

        class WidgetFactory {
        public:
            virtual ~WidgetFactory() = default;
            virtual std::unique_ptr<Button> createButton() const = 0;
            virtual std::unique_ptr<Checkbox> createCheckbox() const = 0;
        };

        class WindowsFactory final : public WidgetFactory {
        public:
            std::unique_ptr<Button> createButton() const override {
                return std::make_unique<WindowsButton>();
            }
            std::unique_ptr<Checkbox> createCheckbox() const override {
                return std::make_unique<WindowsCheckbox>();
            }
        };

        class MacFactory final : public WidgetFactory {
        public:
            std::unique_ptr<Button> createButton() const override {
                return std::make_unique<MacButton>();
            }
            std::unique_ptr<Checkbox> createCheckbox() const override {
                return std::make_unique<MacCheckbox>();
            }
        };

        void renderForm(const WidgetFactory& factory) {
            // One factory creates a compatible family of related products.
            auto button = factory.createButton();
            auto checkbox = factory.createCheckbox();
            button->paint();
            checkbox->paint();
        }

        int main() {
            MacFactory factory;
            renderForm(factory);
        }
        """
    ),
    "lld-1creational-design-pattern-4-builder": cpp(
        r"""
        #include <iostream>
        #include <string>
        #include <utility>

        struct Computer {
            std::string cpu;
            int memoryGb = 0;
            bool hasGpu = false;
        };

        class ComputerBuilder {
        public:
            ComputerBuilder& cpu(std::string value) {
                computer_.cpu = std::move(value);
                return *this;
            }

            ComputerBuilder& memory(int gigabytes) {
                computer_.memoryGb = gigabytes;
                return *this;
            }

            ComputerBuilder& withGpu() {
                computer_.hasGpu = true;
                return *this;
            }

            Computer build() const { return computer_; }

        private:
            Computer computer_;
        };

        int main() {
            // Fluent steps make construction readable without a telescoping constructor.
            Computer pc = ComputerBuilder()
                              .cpu("8-core")
                              .memory(32)
                              .withGpu()
                              .build();
            std::cout << pc.cpu << ", " << pc.memoryGb << " GB, GPU="
                      << std::boolalpha << pc.hasGpu << '\n';
        }
        """
    ),
    "lld-1creational-design-pattern-5-prototype": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        class Shape {
        public:
            virtual ~Shape() = default;
            virtual std::unique_ptr<Shape> clone() const = 0;
            virtual void draw() const = 0;
        };

        class Circle final : public Shape {
        public:
            Circle(int radius, std::string color)
                : radius_(radius), color_(std::move(color)) {}

            std::unique_ptr<Shape> clone() const override {
                // Copying the concrete object preserves its configured state.
                return std::make_unique<Circle>(*this);
            }

            void draw() const override {
                std::cout << color_ << " circle, radius " << radius_ << '\n';
            }

        private:
            int radius_;
            std::string color_;
        };

        int main() {
            Circle original(10, "blue");
            auto copy = original.clone();
            original.draw();
            copy->draw();
        }
        """
    ),
    "lld-2-structural-design-pattern-1-adapter": cpp(
        r"""
        #include <iostream>
        #include <string>
        #include <utility>

        class Printer {
        public:
            virtual ~Printer() = default;
            virtual void print(const std::string& text) const = 0;
        };

        class LegacyPrinter {
        public:
            void printText(const char* text) const {
                std::cout << "Legacy printer: " << text << '\n';
            }
        };

        class PrinterAdapter final : public Printer {
        public:
            explicit PrinterAdapter(LegacyPrinter printer)
                : printer_(std::move(printer)) {}

            void print(const std::string& text) const override {
                // The adapter translates the expected interface to the legacy API.
                printer_.printText(text.c_str());
            }

        private:
            LegacyPrinter printer_;
        };

        int main() {
            PrinterAdapter adapter(LegacyPrinter{});
            adapter.print("adapter in action");
        }
        """
    ),
    "lld-2-structural-design-pattern-2-bridge": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        class Renderer {
        public:
            virtual ~Renderer() = default;
            virtual void renderCircle(double radius) const = 0;
        };

        class VectorRenderer final : public Renderer {
        public:
            void renderCircle(double radius) const override {
                std::cout << "Vector circle, radius " << radius << '\n';
            }
        };

        class RasterRenderer final : public Renderer {
        public:
            void renderCircle(double radius) const override {
                std::cout << "Raster circle, radius " << radius << '\n';
            }
        };

        class Shape {
        public:
            explicit Shape(std::shared_ptr<Renderer> renderer)
                : renderer_(std::move(renderer)) {}
            virtual ~Shape() = default;
            virtual void draw() const = 0;

        protected:
            // The abstraction delegates platform work through this bridge.
            std::shared_ptr<Renderer> renderer_;
        };

        class Circle final : public Shape {
        public:
            Circle(std::shared_ptr<Renderer> renderer, double radius)
                : Shape(std::move(renderer)), radius_(radius) {}

            void draw() const override { renderer_->renderCircle(radius_); }

        private:
            double radius_;
        };

        int main() {
            Circle vectorCircle(std::make_shared<VectorRenderer>(), 5.0);
            Circle rasterCircle(std::make_shared<RasterRenderer>(), 8.0);
            vectorCircle.draw();
            rasterCircle.draw();
        }
        """
    ),
    "lld-2-structural-design-pattern-3-composite": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <numeric>
        #include <string>
        #include <utility>
        #include <vector>

        class FileSystemEntry {
        public:
            virtual ~FileSystemEntry() = default;
            virtual int size() const = 0;
            virtual void show(int indent = 0) const = 0;
        };

        class File final : public FileSystemEntry {
        public:
            File(std::string name, int bytes)
                : name_(std::move(name)), bytes_(bytes) {}

            int size() const override { return bytes_; }
            void show(int indent = 0) const override {
                std::cout << std::string(indent, ' ') << name_ << " (" << bytes_ << ")\n";
            }

        private:
            std::string name_;
            int bytes_;
        };

        class Directory final : public FileSystemEntry {
        public:
            explicit Directory(std::string name) : name_(std::move(name)) {}

            void add(std::unique_ptr<FileSystemEntry> entry) {
                children_.push_back(std::move(entry));
            }

            int size() const override {
                return std::accumulate(
                    children_.begin(), children_.end(), 0,
                    [](int total, const auto& child) { return total + child->size(); });
            }

            void show(int indent = 0) const override {
                std::cout << std::string(indent, ' ') << name_ << "/\n";
                // Leaves and groups share one interface, so clients treat them uniformly.
                for (const auto& child : children_) {
                    child->show(indent + 2);
                }
            }

        private:
            std::string name_;
            std::vector<std::unique_ptr<FileSystemEntry>> children_;
        };

        int main() {
            Directory root("project");
            root.add(std::make_unique<File>("README.md", 12));
            auto source = std::make_unique<Directory>("src");
            source->add(std::make_unique<File>("main.cpp", 42));
            root.add(std::move(source));
            root.show();
            std::cout << "Total: " << root.size() << '\n';
        }
        """
    ),
    "lld-2-structural-design-pattern-4-decorator": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        class Coffee {
        public:
            virtual ~Coffee() = default;
            virtual std::string description() const = 0;
            virtual double cost() const = 0;
        };

        class PlainCoffee final : public Coffee {
        public:
            std::string description() const override { return "coffee"; }
            double cost() const override { return 2.0; }
        };

        class CoffeeDecorator : public Coffee {
        public:
            explicit CoffeeDecorator(std::unique_ptr<Coffee> wrapped)
                : wrapped_(std::move(wrapped)) {}

        protected:
            std::unique_ptr<Coffee> wrapped_;
        };

        class Milk final : public CoffeeDecorator {
        public:
            using CoffeeDecorator::CoffeeDecorator;
            std::string description() const override {
                return wrapped_->description() + ", milk";
            }
            double cost() const override { return wrapped_->cost() + 0.5; }
        };

        class WhippedCream final : public CoffeeDecorator {
        public:
            using CoffeeDecorator::CoffeeDecorator;
            std::string description() const override {
                return wrapped_->description() + ", whipped cream";
            }
            double cost() const override { return wrapped_->cost() + 0.75; }
        };

        int main() {
            // Each decorator adds behavior while preserving the Coffee interface.
            std::unique_ptr<Coffee> drink = std::make_unique<PlainCoffee>();
            drink = std::make_unique<Milk>(std::move(drink));
            drink = std::make_unique<WhippedCream>(std::move(drink));
            std::cout << drink->description() << ": $" << drink->cost() << '\n';
        }
        """
    ),
    "lld-2-structural-design-pattern-5-facade": cpp(
        r"""
        #include <iostream>
        #include <string>

        class Amplifier {
        public:
            void on() const { std::cout << "Amplifier on\n"; }
            void setVolume(int value) const { std::cout << "Volume " << value << '\n'; }
        };

        class Projector {
        public:
            void on() const { std::cout << "Projector on\n"; }
            void wideScreen() const { std::cout << "Widescreen mode\n"; }
        };

        class StreamingPlayer {
        public:
            void on() const { std::cout << "Player on\n"; }
            void play(const std::string& movie) const {
                std::cout << "Playing " << movie << '\n';
            }
        };

        class HomeTheaterFacade {
        public:
            void watchMovie(const std::string& movie) const {
                // The facade presents one operation for a multi-subsystem workflow.
                amplifier_.on();
                amplifier_.setVolume(8);
                projector_.on();
                projector_.wideScreen();
                player_.on();
                player_.play(movie);
            }

        private:
            Amplifier amplifier_;
            Projector projector_;
            StreamingPlayer player_;
        };

        int main() {
            HomeTheaterFacade theater;
            theater.watchMovie("Design Patterns");
        }
        """
    ),
    "lld-2-structural-design-pattern-6-flyweight": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <unordered_map>
        #include <utility>

        class TreeType {
        public:
            TreeType(std::string name, std::string color)
                : name_(std::move(name)), color_(std::move(color)) {}

            void draw(int x, int y) const {
                std::cout << color_ << ' ' << name_ << " at " << x << ',' << y << '\n';
            }

        private:
            std::string name_;
            std::string color_;
        };

        class TreeFactory {
        public:
            std::shared_ptr<const TreeType> get(std::string name, std::string color) {
                const std::string key = name + ':' + color;
                auto [it, inserted] = types_.try_emplace(key, nullptr);
                if (inserted) {
                    // Intrinsic state is created once and shared by many tree instances.
                    it->second = std::make_shared<TreeType>(std::move(name), std::move(color));
                }
                return it->second;
            }

        private:
            std::unordered_map<std::string, std::shared_ptr<const TreeType>> types_;
        };

        struct Tree {
            int x;
            int y;
            std::shared_ptr<const TreeType> type;

            void draw() const { type->draw(x, y); }
        };

        int main() {
            TreeFactory factory;
            Tree first{1, 2, factory.get("oak", "green")};
            Tree second{8, 5, factory.get("oak", "green")};
            first.draw();
            second.draw();
            std::cout << std::boolalpha << (first.type == second.type) << '\n';
        }
        """
    ),
    "lld-2-structural-design-pattern-7-proxy": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        class Image {
        public:
            virtual ~Image() = default;
            virtual void display() = 0;
        };

        class RealImage final : public Image {
        public:
            explicit RealImage(std::string filename) : filename_(std::move(filename)) {
                std::cout << "Loading " << filename_ << '\n';
            }

            void display() override { std::cout << "Displaying " << filename_ << '\n'; }

        private:
            std::string filename_;
        };

        class ImageProxy final : public Image {
        public:
            explicit ImageProxy(std::string filename) : filename_(std::move(filename)) {}

            void display() override {
                // The proxy delays creation of the expensive real object until first use.
                if (!real_) {
                    real_ = std::make_unique<RealImage>(filename_);
                }
                real_->display();
            }

        private:
            std::string filename_;
            std::unique_ptr<RealImage> real_;
        };

        int main() {
            ImageProxy image("photo.png");
            image.display();
            image.display();
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-1-chain-of-responsibility": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        class Handler {
        public:
            virtual ~Handler() = default;

            Handler& setNext(std::unique_ptr<Handler> next) {
                next_ = std::move(next);
                return *next_;
            }

            virtual bool handle(int amount) const {
                // An unhandled request continues along the chain.
                return next_ ? next_->handle(amount) : false;
            }

        private:
            std::unique_ptr<Handler> next_;
        };

        class Manager final : public Handler {
        public:
            bool handle(int amount) const override {
                if (amount <= 1'000) {
                    std::cout << "Manager approved " << amount << '\n';
                    return true;
                }
                return Handler::handle(amount);
            }
        };

        class Director final : public Handler {
        public:
            bool handle(int amount) const override {
                if (amount <= 10'000) {
                    std::cout << "Director approved " << amount << '\n';
                    return true;
                }
                return Handler::handle(amount);
            }
        };

        int main() {
            auto manager = std::make_unique<Manager>();
            manager->setNext(std::make_unique<Director>());
            std::cout << std::boolalpha << manager->handle(5'000) << '\n';
            std::cout << std::boolalpha << manager->handle(50'000) << '\n';
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-2-command": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <utility>
        #include <vector>

        class Light {
        public:
            void on() { std::cout << "Light on\n"; }
            void off() { std::cout << "Light off\n"; }
        };

        class Command {
        public:
            virtual ~Command() = default;
            virtual void execute() = 0;
            virtual void undo() = 0;
        };

        class TurnOn final : public Command {
        public:
            explicit TurnOn(Light& light) : light_(light) {}
            void execute() override { light_.on(); }
            void undo() override { light_.off(); }

        private:
            Light& light_;
        };

        class Remote {
        public:
            void submit(std::unique_ptr<Command> command) {
                // The request is an object, so it can be stored and undone later.
                command->execute();
                history_.push_back(std::move(command));
            }

            void undoLast() {
                if (!history_.empty()) {
                    history_.back()->undo();
                    history_.pop_back();
                }
            }

        private:
            std::vector<std::unique_ptr<Command>> history_;
        };

        int main() {
            Light light;
            Remote remote;
            remote.submit(std::make_unique<TurnOn>(light));
            remote.undoLast();
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-3-interpreter": cpp(
        r"""
        #include <iostream>
        #include <memory>

        class Expression {
        public:
            virtual ~Expression() = default;
            virtual int interpret() const = 0;
        };

        class Number final : public Expression {
        public:
            explicit Number(int value) : value_(value) {}
            int interpret() const override { return value_; }

        private:
            int value_;
        };

        class Add final : public Expression {
        public:
            Add(std::unique_ptr<Expression> left, std::unique_ptr<Expression> right)
                : left_(std::move(left)), right_(std::move(right)) {}

            int interpret() const override {
                return left_->interpret() + right_->interpret();
            }

        private:
            // The expression tree is the parsed representation of the tiny language.
            std::unique_ptr<Expression> left_;
            std::unique_ptr<Expression> right_;
        };

        int main() {
            auto expression = std::make_unique<Add>(
                std::make_unique<Number>(7),
                std::make_unique<Number>(5));
            std::cout << expression->interpret() << '\n';
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-4-iterator": cpp(
        r"""
        #include <cstddef>
        #include <iostream>
        #include <stdexcept>
        #include <vector>

        class NumberCollection {
        public:
            class Iterator {
            public:
                Iterator(const NumberCollection& owner, std::size_t index)
                    : owner_(owner), index_(index) {}

                bool hasNext() const { return index_ < owner_.values_.size(); }

                int next() {
                    if (!hasNext()) {
                        throw std::out_of_range("iterator exhausted");
                    }
                    return owner_.values_[index_++];
                }

            private:
                const NumberCollection& owner_;
                std::size_t index_;
            };

            void add(int value) { values_.push_back(value); }
            Iterator iterator() const {
                // Traversal state lives in the iterator, not in the collection.
                return Iterator(*this, 0);
            }

        private:
            std::vector<int> values_;
        };

        int main() {
            NumberCollection numbers;
            numbers.add(10);
            numbers.add(20);
            auto it = numbers.iterator();
            while (it.hasNext()) {
                std::cout << it.next() << '\n';
            }
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-5-mediator": cpp(
        r"""
        #include <iostream>
        #include <string>
        #include <vector>

        class Participant;

        class ChatRoom {
        public:
            void join(Participant& participant) { participants_.push_back(&participant); }
            void broadcast(const Participant& sender, const std::string& message) const;

        private:
            std::vector<Participant*> participants_;
        };

        class Participant {
        public:
            Participant(std::string name, ChatRoom& room)
                : name_(std::move(name)), room_(room) {
                room_.join(*this);
            }

            void send(const std::string& message) const {
                room_.broadcast(*this, message);
            }

            void receive(const std::string& message) const {
                std::cout << name_ << " received: " << message << '\n';
            }

        private:
            std::string name_;
            ChatRoom& room_;
        };

        void ChatRoom::broadcast(
            const Participant& sender, const std::string& message) const {
            // Colleagues communicate through the mediator instead of referencing each other.
            for (const Participant* participant : participants_) {
                if (participant != &sender) {
                    participant->receive(message);
                }
            }
        }

        int main() {
            ChatRoom room;
            Participant alice("Alice", room);
            Participant bob("Bob", room);
            alice.send("Hello");
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-6-memento": cpp(
        r"""
        #include <iostream>
        #include <string>
        #include <utility>
        #include <vector>

        class Editor {
        public:
            class Memento {
                friend class Editor;
                explicit Memento(std::string text) : text_(std::move(text)) {}
                std::string text_;
            };

            void type(std::string text) { text_ += std::move(text); }
            Memento save() const { return Memento(text_); }
            void restore(const Memento& snapshot) { text_ = snapshot.text_; }
            const std::string& text() const { return text_; }

        private:
            std::string text_;
        };

        int main() {
            Editor editor;
            editor.type("first draft");
            // The opaque memento captures state without exposing the originator's internals.
            auto checkpoint = editor.save();
            editor.type(" with mistakes");
            editor.restore(checkpoint);
            std::cout << editor.text() << '\n';
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-7-observer-pub-sub": cpp(
        r"""
        #include <algorithm>
        #include <iostream>
        #include <vector>

        class Observer {
        public:
            virtual ~Observer() = default;
            virtual void update(int temperature) = 0;
        };

        class WeatherStation {
        public:
            void subscribe(Observer& observer) { observers_.push_back(&observer); }

            void unsubscribe(Observer& observer) {
                observers_.erase(
                    std::remove(observers_.begin(), observers_.end(), &observer),
                    observers_.end());
            }

            void setTemperature(int value) {
                temperature_ = value;
                // The subject broadcasts changes without knowing concrete observers.
                for (Observer* observer : observers_) {
                    observer->update(temperature_);
                }
            }

        private:
            int temperature_ = 0;
            std::vector<Observer*> observers_;
        };

        class PhoneDisplay final : public Observer {
        public:
            void update(int temperature) override {
                std::cout << "Phone: " << temperature << " C\n";
            }
        };

        int main() {
            WeatherStation station;
            PhoneDisplay phone;
            station.subscribe(phone);
            station.setTemperature(24);
            station.unsubscribe(phone);
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-8-state": cpp(
        r"""
        #include <iostream>
        #include <memory>

        class Turnstile;

        class State {
        public:
            virtual ~State() = default;
            virtual void insertCoin(Turnstile& turnstile) const = 0;
            virtual void push(Turnstile& turnstile) const = 0;
        };

        class Turnstile {
        public:
            explicit Turnstile(std::unique_ptr<State> state)
                : state_(std::move(state)) {}

            void setState(std::unique_ptr<State> state) { state_ = std::move(state); }
            void insertCoin() { state_->insertCoin(*this); }
            void push() { state_->push(*this); }

        private:
            std::unique_ptr<State> state_;
        };

        class Unlocked;

        class Locked final : public State {
        public:
            void insertCoin(Turnstile& turnstile) const override;
            void push(Turnstile&) const override {
                std::cout << "Blocked\n";
            }
        };

        class Unlocked final : public State {
        public:
            void insertCoin(Turnstile&) const override {
                std::cout << "Coin returned\n";
            }
            void push(Turnstile& turnstile) const override {
                std::cout << "Passed\n";
                turnstile.setState(std::make_unique<Locked>());
            }
        };

        void Locked::insertCoin(Turnstile& turnstile) const {
            // Changing the state object changes the turnstile's behavior.
            std::cout << "Unlocked\n";
            turnstile.setState(std::make_unique<Unlocked>());
        }

        int main() {
            Turnstile turnstile(std::make_unique<Locked>());
            turnstile.push();
            turnstile.insertCoin();
            turnstile.push();
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-9-strategy": cpp(
        r"""
        #include <algorithm>
        #include <iostream>
        #include <memory>
        #include <vector>

        class SortStrategy {
        public:
            virtual ~SortStrategy() = default;
            virtual void sort(std::vector<int>& values) const = 0;
        };

        class Ascending final : public SortStrategy {
        public:
            void sort(std::vector<int>& values) const override {
                std::sort(values.begin(), values.end());
            }
        };

        class Descending final : public SortStrategy {
        public:
            void sort(std::vector<int>& values) const override {
                std::sort(values.rbegin(), values.rend());
            }
        };

        class NumberList {
        public:
            explicit NumberList(std::unique_ptr<SortStrategy> strategy)
                : strategy_(std::move(strategy)) {}

            void setStrategy(std::unique_ptr<SortStrategy> strategy) {
                strategy_ = std::move(strategy);
            }

            void sort(std::vector<int>& values) const {
                // The algorithm is interchangeable independently of the context.
                strategy_->sort(values);
            }

        private:
            std::unique_ptr<SortStrategy> strategy_;
        };

        int main() {
            std::vector<int> values{3, 1, 2};
            NumberList list(std::make_unique<Ascending>());
            list.sort(values);
            list.setStrategy(std::make_unique<Descending>());
            list.sort(values);
            for (int value : values) {
                std::cout << value << ' ';
            }
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-10-template-method": cpp(
        r"""
        #include <iostream>

        class DataExporter {
        public:
            virtual ~DataExporter() = default;

            void exportData() const {
                // The base class fixes the algorithm skeleton; subclasses fill selected steps.
                connect();
                writeHeader();
                writeRows();
                disconnect();
            }

        protected:
            void connect() const { std::cout << "Connect\n"; }
            virtual void writeHeader() const = 0;
            virtual void writeRows() const = 0;
            void disconnect() const { std::cout << "Disconnect\n"; }
        };

        class CsvExporter final : public DataExporter {
        protected:
            void writeHeader() const override { std::cout << "id,name\n"; }
            void writeRows() const override { std::cout << "1,Ada\n"; }
        };

        int main() {
            CsvExporter exporter;
            exporter.exportData();
        }
        """
    ),
    "lld-3behavioral-design-patterns-object-interactions-11-visitor": cpp(
        r"""
        #include <iostream>

        class Circle;
        class Rectangle;

        class ShapeVisitor {
        public:
            virtual ~ShapeVisitor() = default;
            virtual void visit(const Circle& circle) = 0;
            virtual void visit(const Rectangle& rectangle) = 0;
        };

        class Shape {
        public:
            virtual ~Shape() = default;
            virtual void accept(ShapeVisitor& visitor) const = 0;
        };

        class Circle final : public Shape {
        public:
            explicit Circle(double radius) : radius_(radius) {}
            double radius() const { return radius_; }
            void accept(ShapeVisitor& visitor) const override { visitor.visit(*this); }

        private:
            double radius_;
        };

        class Rectangle final : public Shape {
        public:
            Rectangle(double width, double height) : width_(width), height_(height) {}
            double width() const { return width_; }
            double height() const { return height_; }
            void accept(ShapeVisitor& visitor) const override { visitor.visit(*this); }

        private:
            double width_;
            double height_;
        };

        class AreaVisitor final : public ShapeVisitor {
        public:
            void visit(const Circle& circle) override {
                result_ = 3.14159 * circle.radius() * circle.radius();
            }
            void visit(const Rectangle& rectangle) override {
                result_ = rectangle.width() * rectangle.height();
            }
            double result() const { return result_; }

        private:
            double result_ = 0.0;
        };

        int main() {
            Circle circle(2.0);
            AreaVisitor area;
            // Double dispatch selects behavior by both visitor and element type.
            circle.accept(area);
            std::cout << area.result() << '\n';
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-1-thread-pool": cpp(
        r"""
        #include <condition_variable>
        #include <cstddef>
        #include <functional>
        #include <future>
        #include <iostream>
        #include <memory>
        #include <mutex>
        #include <queue>
        #include <stdexcept>
        #include <thread>
        #include <type_traits>
        #include <utility>
        #include <vector>

        class ThreadPool {
        public:
            explicit ThreadPool(std::size_t count) {
                for (std::size_t i = 0; i < count; ++i) {
                    workers_.emplace_back([this] {
                        for (;;) {
                            std::function<void()> task;
                            {
                                std::unique_lock<std::mutex> lock(mutex_);
                                ready_.wait(lock, [this] { return stopping_ || !tasks_.empty(); });
                                if (stopping_ && tasks_.empty()) {
                                    return;
                                }
                                task = std::move(tasks_.front());
                                tasks_.pop();
                            }
                            task();
                        }
                    });
                }
            }

            template <class Function>
            auto submit(Function&& function) {
                using Result = std::invoke_result_t<Function>;
                auto task = std::make_shared<std::packaged_task<Result()>>(
                    std::forward<Function>(function));
                std::future<Result> result = task->get_future();
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    if (stopping_) {
                        throw std::runtime_error("thread pool is stopping");
                    }
                    tasks_.push([task] { (*task)(); });
                }
                ready_.notify_one();
                return result;
            }

            ~ThreadPool() {
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    stopping_ = true;
                }
                ready_.notify_all();
                for (auto& worker : workers_) {
                    worker.join();
                }
            }

        private:
            // Workers reuse a bounded set of threads to consume queued tasks.
            std::vector<std::thread> workers_;
            std::queue<std::function<void()>> tasks_;
            std::mutex mutex_;
            std::condition_variable ready_;
            bool stopping_ = false;
        };

        int main() {
            ThreadPool pool(2);
            auto answer = pool.submit([] { return 6 * 7; });
            std::cout << answer.get() << '\n';
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-2-producer-consumer": cpp(
        r"""
        #include <condition_variable>
        #include <cstddef>
        #include <iostream>
        #include <mutex>
        #include <optional>
        #include <queue>
        #include <thread>

        template <class T>
        class BlockingQueue {
        public:
            explicit BlockingQueue(std::size_t capacity) : capacity_(capacity) {}

            void push(T value) {
                std::unique_lock<std::mutex> lock(mutex_);
                notFull_.wait(lock, [this] { return closed_ || queue_.size() < capacity_; });
                if (closed_) {
                    return;
                }
                queue_.push(std::move(value));
                notEmpty_.notify_one();
            }

            std::optional<T> pop() {
                std::unique_lock<std::mutex> lock(mutex_);
                notEmpty_.wait(lock, [this] { return closed_ || !queue_.empty(); });
                if (queue_.empty()) {
                    return std::nullopt;
                }
                T value = std::move(queue_.front());
                queue_.pop();
                notFull_.notify_one();
                return value;
            }

            void close() {
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    closed_ = true;
                }
                // Closing wakes both producers and consumers so neither can wait forever.
                notEmpty_.notify_all();
                notFull_.notify_all();
            }

        private:
            std::size_t capacity_;
            std::queue<T> queue_;
            std::mutex mutex_;
            std::condition_variable notEmpty_;
            std::condition_variable notFull_;
            bool closed_ = false;
        };

        int main() {
            BlockingQueue<int> queue(2);
            std::thread producer([&] {
                for (int value = 1; value <= 3; ++value) {
                    queue.push(value);
                }
                queue.close();
            });
            std::thread consumer([&] {
                while (auto value = queue.pop()) {
                    std::cout << *value << '\n';
                }
            });
            producer.join();
            consumer.join();
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-3-read-write-lock": cpp(
        r"""
        #include <iostream>
        #include <mutex>
        #include <shared_mutex>
        #include <string>
        #include <thread>
        #include <unordered_map>

        class PhoneBook {
        public:
            void put(std::string name, std::string number) {
                // Writers take exclusive ownership.
                std::unique_lock<std::shared_mutex> lock(mutex_);
                entries_[std::move(name)] = std::move(number);
            }

            std::string get(const std::string& name) const {
                // Multiple readers may hold shared ownership concurrently.
                std::shared_lock<std::shared_mutex> lock(mutex_);
                auto it = entries_.find(name);
                return it == entries_.end() ? "missing" : it->second;
            }

        private:
            mutable std::shared_mutex mutex_;
            std::unordered_map<std::string, std::string> entries_;
        };

        int main() {
            PhoneBook book;
            book.put("Ada", "123");
            std::thread first([&] { std::cout << book.get("Ada") << '\n'; });
            std::thread second([&] { std::cout << book.get("Ada") << '\n'; });
            first.join();
            second.join();
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-4-future-promise": cpp(
        r"""
        #include <chrono>
        #include <future>
        #include <iostream>
        #include <thread>

        void compute(std::promise<int> result) {
            try {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
                result.set_value(6 * 7);
            } catch (...) {
                result.set_exception(std::current_exception());
            }
        }

        int main() {
            std::promise<int> promise;
            // The future is the consumer side of the one-time asynchronous result.
            std::future<int> future = promise.get_future();
            std::thread worker(compute, std::move(promise));
            std::cout << "Result: " << future.get() << '\n';
            worker.join();
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-5-monitor": cpp(
        r"""
        #include <condition_variable>
        #include <iostream>
        #include <mutex>
        #include <thread>

        class BankAccount {
        public:
            void deposit(int amount) {
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    balance_ += amount;
                }
                fundsAvailable_.notify_all();
            }

            void withdraw(int amount) {
                std::unique_lock<std::mutex> lock(mutex_);
                fundsAvailable_.wait(lock, [this, amount] { return balance_ >= amount; });
                balance_ -= amount;
            }

            int balance() const {
                std::lock_guard<std::mutex> lock(mutex_);
                return balance_;
            }

        private:
            // State, mutual exclusion, and the wait condition are encapsulated together.
            mutable std::mutex mutex_;
            std::condition_variable fundsAvailable_;
            int balance_ = 0;
        };

        int main() {
            BankAccount account;
            std::thread customer([&] { account.withdraw(50); });
            std::thread teller([&] { account.deposit(75); });
            customer.join();
            teller.join();
            std::cout << account.balance() << '\n';
        }
        """
    ),
    "lld-4concurrency-multithreading-patterns-6-active-object": cpp(
        r"""
        #include <condition_variable>
        #include <functional>
        #include <iostream>
        #include <mutex>
        #include <queue>
        #include <thread>
        #include <utility>

        class ActiveObject {
        public:
            ActiveObject() : worker_([this] { run(); }) {}

            void post(std::function<void()> methodRequest) {
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    requests_.push(std::move(methodRequest));
                }
                ready_.notify_one();
            }

            ~ActiveObject() {
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    stopping_ = true;
                }
                ready_.notify_one();
                worker_.join();
            }

        private:
            void run() {
                for (;;) {
                    std::function<void()> request;
                    {
                        std::unique_lock<std::mutex> lock(mutex_);
                        ready_.wait(lock, [this] { return stopping_ || !requests_.empty(); });
                        if (stopping_ && requests_.empty()) {
                            return;
                        }
                        request = std::move(requests_.front());
                        requests_.pop();
                    }
                    // Method requests execute sequentially on the object's private thread.
                    request();
                }
            }

            std::queue<std::function<void()>> requests_;
            std::mutex mutex_;
            std::condition_variable ready_;
            bool stopping_ = false;
            std::thread worker_;
        };

        int main() {
            ActiveObject logger;
            logger.post([] { std::cout << "first request\n"; });
            logger.post([] { std::cout << "second request\n"; });
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-1-dao-data-access-object": cpp(
        r"""
        #include <iostream>
        #include <optional>
        #include <string>
        #include <unordered_map>
        #include <utility>

        struct User {
            int id;
            std::string name;
        };

        class UserDao {
        public:
            virtual ~UserDao() = default;
            virtual void save(User user) = 0;
            virtual std::optional<User> findById(int id) const = 0;
        };

        class InMemoryUserDao final : public UserDao {
        public:
            void save(User user) override {
                users_.insert_or_assign(user.id, std::move(user));
            }

            std::optional<User> findById(int id) const override {
                auto it = users_.find(id);
                return it == users_.end() ? std::nullopt : std::optional<User>(it->second);
            }

        private:
            // Persistence details stay behind the DAO contract.
            std::unordered_map<int, User> users_;
        };

        int main() {
            InMemoryUserDao dao;
            dao.save({1, "Ada"});
            if (auto user = dao.findById(1)) {
                std::cout << user->name << '\n';
            }
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-2-repository": cpp(
        r"""
        #include <algorithm>
        #include <iostream>
        #include <optional>
        #include <string>
        #include <utility>
        #include <vector>

        struct Product {
            int id;
            std::string name;
            bool inStock;
        };

        class ProductRepository {
        public:
            virtual ~ProductRepository() = default;
            virtual void add(Product product) = 0;
            virtual std::optional<Product> byId(int id) const = 0;
            virtual std::vector<Product> available() const = 0;
        };

        class InMemoryProductRepository final : public ProductRepository {
        public:
            void add(Product product) override { products_.push_back(std::move(product)); }

            std::optional<Product> byId(int id) const override {
                auto it = std::find_if(products_.begin(), products_.end(),
                                       [id](const Product& product) { return product.id == id; });
                return it == products_.end() ? std::nullopt : std::optional<Product>(*it);
            }

            std::vector<Product> available() const override {
                std::vector<Product> result;
                std::copy_if(products_.begin(), products_.end(), std::back_inserter(result),
                             [](const Product& product) { return product.inStock; });
                return result;
            }

        private:
            // Repository methods use domain language rather than storage operations.
            std::vector<Product> products_;
        };

        int main() {
            InMemoryProductRepository products;
            products.add({1, "Keyboard", true});
            products.add({2, "Monitor", false});
            std::cout << products.available().front().name << '\n';
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-3-service-locator": cpp(
        r"""
        #include <iostream>
        #include <memory>
        #include <stdexcept>
        #include <string>
        #include <unordered_map>
        #include <utility>

        class Service {
        public:
            virtual ~Service() = default;
            virtual void execute() const = 0;
        };

        class EmailService final : public Service {
        public:
            void execute() const override { std::cout << "Email sent\n"; }
        };

        class ServiceLocator {
        public:
            void registerService(std::string name, std::shared_ptr<Service> service) {
                services_[std::move(name)] = std::move(service);
            }

            std::shared_ptr<Service> locate(const std::string& name) const {
                auto it = services_.find(name);
                if (it == services_.end()) {
                    throw std::out_of_range("service not registered: " + name);
                }
                return it->second;
            }

        private:
            // Clients request a service by key instead of constructing its implementation.
            std::unordered_map<std::string, std::shared_ptr<Service>> services_;
        };

        int main() {
            ServiceLocator locator;
            locator.registerService("email", std::make_shared<EmailService>());
            locator.locate("email")->execute();
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-4-dependency-injection-di": cpp(
        r"""
        #include <iostream>
        #include <memory>

        class MessageSender {
        public:
            virtual ~MessageSender() = default;
            virtual void send() const = 0;
        };

        class EmailSender final : public MessageSender {
        public:
            void send() const override { std::cout << "Sending email\n"; }
        };

        class NotificationService {
        public:
            // Constructor injection makes the dependency explicit and replaceable.
            explicit NotificationService(std::shared_ptr<MessageSender> sender)
                : sender_(std::move(sender)) {}

            void notify() const { sender_->send(); }

        private:
            std::shared_ptr<MessageSender> sender_;
        };

        int main() {
            auto sender = std::make_shared<EmailSender>();
            NotificationService notifications(sender);
            notifications.notify();
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-5-mvc-model-view-controller": cpp(
        r"""
        #include <iostream>
        #include <string>
        #include <utility>

        class TodoModel {
        public:
            void setTitle(std::string title) { title_ = std::move(title); }
            const std::string& title() const { return title_; }

        private:
            std::string title_;
        };

        class TodoView {
        public:
            void render(const TodoModel& model) const {
                std::cout << "Todo: " << model.title() << '\n';
            }
        };

        class TodoController {
        public:
            TodoController(TodoModel& model, TodoView& view) : model_(model), view_(view) {}

            void rename(std::string title) {
                // The controller handles input, updates the model, then selects the view.
                model_.setTitle(std::move(title));
                view_.render(model_);
            }

        private:
            TodoModel& model_;
            TodoView& view_;
        };

        int main() {
            TodoModel model;
            TodoView view;
            TodoController controller(model, view);
            controller.rename("Study MVC");
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-6-mvvm-model-view-viewmodel": cpp(
        r"""
        #include <functional>
        #include <iostream>
        #include <string>
        #include <utility>

        class UserModel {
        public:
            std::string firstName;
            std::string lastName;
        };

        class UserViewModel {
        public:
            explicit UserViewModel(UserModel model) : model_(std::move(model)) {}

            std::string displayName() const {
                return model_.lastName + ", " + model_.firstName;
            }

            void rename(std::string first, std::string last) {
                model_.firstName = std::move(first);
                model_.lastName = std::move(last);
                if (changed_) {
                    // A binding callback lets the view react without owning domain logic.
                    changed_(displayName());
                }
            }

            void bind(std::function<void(const std::string&)> changed) {
                changed_ = std::move(changed);
            }

        private:
            UserModel model_;
            std::function<void(const std::string&)> changed_;
        };

        int main() {
            UserViewModel viewModel({"Ada", "Lovelace"});
            viewModel.bind([](const std::string& text) {
                std::cout << "View: " << text << '\n';
            });
            viewModel.rename("Grace", "Hopper");
        }
        """
    ),
    "lld-5architectural-enterprise-patterns-7-observerevent-bus": cpp(
        r"""
        #include <functional>
        #include <iostream>
        #include <string>
        #include <unordered_map>
        #include <utility>
        #include <vector>

        class EventBus {
        public:
            using Handler = std::function<void(const std::string&)>;

            void subscribe(std::string topic, Handler handler) {
                handlers_[std::move(topic)].push_back(std::move(handler));
            }

            void publish(const std::string& topic, const std::string& payload) const {
                auto it = handlers_.find(topic);
                if (it == handlers_.end()) {
                    return;
                }
                // Publishers and subscribers are decoupled by the topic-based bus.
                for (const Handler& handler : it->second) {
                    handler(payload);
                }
            }

        private:
            std::unordered_map<std::string, std::vector<Handler>> handlers_;
        };

        int main() {
            EventBus bus;
            bus.subscribe("order.created", [](const std::string& orderId) {
                std::cout << "Reserve stock for " << orderId << '\n';
            });
            bus.subscribe("order.created", [](const std::string& orderId) {
                std::cout << "Send receipt for " << orderId << '\n';
            });
            bus.publish("order.created", "A-42");
        }
        """
    ),
}


TARGET_CATEGORY_PREFIXES = (
    "lld-1creational",
    "lld-2-structural",
    "lld-3behavioral",
    "lld-4concurrency",
    "lld-5architectural",
)
